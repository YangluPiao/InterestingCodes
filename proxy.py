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
extract_reply=re.compile('GET.*HTTP/1\.1')
extract_segment=re.compile('GET /vod/.*Seg.* HTTP/1\.1')

def browse(Cli_Sock):
    global BUFF_SIZE
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # send_sock.bind(('',8080))
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
        # length=1
        # loop_start=time.time()
        loop_enabled=True
        while loop_enabled:
            loop_start=time.time()
            inputready, outputready, exceptready = select.select(input_list,[],[])
            # if inputready:
            for input_item in inputready:
                start_time=time.time()
                reply = input_item.recv(BUFF_SIZE)
                end_time=time.time()
                result=extract_reply.match(reply)
                
                if input_item==Cli_Sock:                   
                    send_sock.sendall(reply)
                    if result is not None:
                        result=result.group()
                        digits=extract_segment.match(reply)
                        if digits is not None:
                            digits=digits.group()
                            # digits=re.findall(r'\d+',digits)
                            # bit=digits
                        print result
                        print 'bitrate is: %f Mbs'%(BUFF_SIZE*8/((end_time-start_time)*10**6))
                        
                    else:
                        # print reply
                        print 'thread finished'
                        loop_enabled=False
                    # print 'client data:%s'%reply
                elif input_item==send_sock:
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
            Cli_Sock, Cli_addr = Serv_Sock.accept() # Accept a connection from client
            # print addr
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
    

    
