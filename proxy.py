import socket
import sys,os
import select,threading,time,re


if len(sys.argv) <= 1: 
    print 'Usage: \'python proxy.py port\'\n[port : It is the port of the Proxy Server'
    sys.exit(2)

# Server socket created, bound and starting to listen
Serv_Port = int(sys.argv[1]) # sys.argv[1] is the port number entered by the user
Serv_Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # socket.socket function creates a socket.
Serv_Sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# Prepare a server socket
print 'Starting server ....'
Serv_Sock.bind(('', Serv_Port))
Serv_Sock.listen(5)
Serv_Sock.settimeout(None)
extract_reply=re.compile(r'GET.*HTTP/1\.1')
extract_segment=re.compile(r'GET /vod/.*Seg.* HTTP/1\.1')
content_length_re=re.compile(r'Content-Length: \d+')
alpha=0.5
throughput=None
def browse(Cli_Sock):
    global BUFF_SIZE
    global throughput
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        
        send_sock.bind(('1.0.0.1',0))
        send_sock.settimeout(None)
        send_sock.connect(('3.0.0.1',80))
        # message = (
        #     'GET / HTTP/1.0\r\n'
        #     'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0\r\n'
        #     'Connection: keep-alive\r\n\r\n'
        #     )
        # send_sock.sendall(message)
        # reply=send_sock.recv(BUFF_SIZE)
        # Cli_Sock.sendall(reply)
        input_list=[Cli_Sock,send_sock]
        loop_enabled=True
        chunk_start=0
        chunk_end=0
        
        while loop_enabled:  
            inputready, outputready, exceptready = select.select(input_list,[],[])
            for input_item in inputready:
                reply = input_item.recv(BUFF_SIZE)
                result=re.findall(extract_reply,reply)
                if input_item==Cli_Sock:
                    fake_bunny=len(re.findall(r'big\_buck\_bunny',reply))>0
                    if fake_bunny:
                        make_up=(
                            'GET /vod/big_buck_bunny_nolist.f4m HTTP/1.0\r\n\r\n'
                            )
                        send_sock.sendall(make_up)
                    else:
                        send_sock.sendall(reply)
                    received=send_sock.recv(BUFF_SIZE)
                    Cli_Sock.sendall(received)
                    received=received[:200]
                    if result is not None and len(result)>0:
                        if not fake_bunny:
                            print result[0]
                        if extract_segment.match(reply) is not None:
                            
                            curr_file=re.findall(r'\d+Seg.*Frag\d+',result[0])[0]
                            try:
                                content_length=re.findall(content_length_re, received)
                                if content_length is not None:
                                    file_bytes=re.findall(r'\d+',content_length[0])
                                    curr_file_size=file_bytes[0]
                                    new_chunk_start=time.time()
                            except Exception,e:
                                print e
                            if chunk_start<chunk_end:
                                trans_time=chunk_end-chunk_start
                                throughput_new=int(curr_file_size)/trans_time/(1000**2)
                                if not throughput:
                                    throughput=throughput_new
                                else:
                                    throughput=alpha*(throughput_new)+(1-alpha)*throughput
                                print 'trasnmission time is %fs, bitrate is %.2f(%.2f) MB/s'%(trans_time,throughput,throughput_new)
                            print 'file \'%s\' is %s byte'%(curr_file,curr_file_size)
                            chunk_start=new_chunk_start
                    else:
                        # print reply
                        print 'thread finished'
                        loop_enabled=False
                    # print 'client data:%s'%reply
                elif input_item==send_sock:
                    if chunk_start>0:
                        chunk_end=time.time()
                    Cli_Sock.sendall(reply)
    except socket.timeout:
        print 'socket timeout'
    except socket.error:
        print 'socket error'   
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print exc_type, fname, exc_tb.tb_lineno
    send_sock.close()
    Cli_Sock.close()
def main():
    try:
        while True:
            # Start receiving data from the client
            print 'ready to accept...'
            Cli_Sock, Cli_addr = Serv_Sock.accept() # Accept a connection from client
            print 'Connection received from: ', Cli_addr
            # browse(Cli_Sock)
            t=threading.Thread(target=browse,args=(Cli_Sock,))
            t.daemon=True
            t.start()
            print 'current living thread: %d'%threading.activeCount()      
    except KeyboardInterrupt:
        print 'Closing server...'
        Serv_Sock.close()
        sys.exit()
if __name__ == '__main__':
    BUFF_SIZE=1024
    main()
    

    
