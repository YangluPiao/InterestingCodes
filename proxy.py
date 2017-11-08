import socket
import sys,os
import select,threading,time,re



class proxy(object):
    def __init__(self, port=8000,alpha=0.5,fake_ip='1.0.0.1',server_ip='3.0.0.1'):
        # Set proxy listening socket
        self.Serv_Sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Close connection immediately after program ends
        self.Serv_Sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print 'Starting server ....'
        self.Serv_Sock.bind(('', port))
        self.Serv_Sock.listen(5)
        self.Serv_Sock.settimeout(None)
        # Set default parameters
        self.BUFF_SIZE=1024
        self.throughput=None
        self.alpha=alpha
        self.fake_ip=fake_ip
        self.server_ip=server_ip
        # Set regex
        self.extract_reply=re.compile(r'GET.*HTTP/1\.1')
        self.extract_segment=re.compile(r'GET /vod/.*Seg.* HTTP/1\.1')
        self.content_length_re=re.compile(r'Content-Length: \d+')
    def listen(self):
        try:
            while True:
                # Start receiving data from the client
                print 'ready to accept...'
                Cli_Sock, Cli_addr = self.Serv_Sock.accept() # Accept a connection from client
                print 'Connection received from: ', Cli_addr
                # Use threads
                t=threading.Thread(target=self.proxy2server,args=(Cli_Sock,))
                t.daemon=True
                t.start()
                print 'current living thread: %d'%threading.activeCount() 
        except KeyboardInterrupt:
            # If ctrl-c is captured then close proxy server
            print 'Closing server...'
            self.Serv_Sock.close()
            sys.exit()
    def init_send_socket(self):
        # Initialize sending socket of proxy server
        send_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        send_sock.bind((self.fake_ip,0))
        send_sock.settimeout(None)
        send_sock.connect((self.server_ip,80))
        return send_sock
    def proxy2server(self,Cli_Sock):
        send_sock = self.init_send_socket()
        try:
            # Possible input requests, one is for client(browser), the other one is for the server
            input_list=[Cli_Sock,send_sock]
            loop_enabled=True
            # Record timestamps at which transmission of a chunk starts and ends
            chunk_start=0
            chunk_end=0
            while loop_enabled:  
                inputready, outputready, exceptready = select.select(input_list,[],[])
                for input_item in inputready:
                    reply = input_item.recv(self.BUFF_SIZE)
                    # Find all the 'GET' in requests
                    result=re.findall(self.extract_reply,reply)
                    # If request is from client, forward to server
                    if input_item==Cli_Sock:
                        # Find big_buck_bunny.f4m in the header
                        fake_bunny=len(re.findall(r'big\_buck\_bunny',reply))>0
                        if fake_bunny:
                            # If found, request big_buck_bunny_nolist.f4m instead
                            make_up=(
                                'GET /vod/big_buck_bunny_nolist.f4m HTTP/1.0\r\n\r\n'
                                )
                            send_sock.sendall(make_up)
                        else:
                            send_sock.sendall(reply)
                        # Send request to the server
                        received=send_sock.recv(self.BUFF_SIZE)
                        # Forward response from server to the client
                        Cli_Sock.sendall(received)
                        received=received[:200]
                        # If 'GET' is found
                        if result is not None and len(result)>0:
                            if not fake_bunny:
                                print result[0]
                            # If 'GET' is requesting video chunks
                            if self.extract_segment.match(reply) is not None:
                                curr_file=re.findall(r'\d+Seg.*Frag\d+',result[0])[0]
                                content_length=re.findall(self.content_length_re, received)
                                if content_length is not None:
                                    file_bytes=re.findall(r'\d+',content_length[0])
                                    curr_file_size=file_bytes[0]
                                    new_chunk_start=time.time()
                                # Calculate throughput for LAST file
                                if chunk_start<chunk_end:
                                    trans_time=chunk_end-chunk_start
                                    throughput_new=int(curr_file_size)/trans_time/(1000**2)
                                    if not self.throughput:
                                        self.throughput=throughput_new
                                    else:
                                        self.throughput=self.alpha*(throughput_new)+(1-self.alpha)*self.throughput
                                    print 'trasnmission time is %fs, bitrate is %.2f(%.2f) MB/s'%(trans_time,self.throughput,throughput_new)
                                print 'file \'%s\' is %s byte'%(curr_file,curr_file_size)
                                chunk_start=new_chunk_start
                        else:
                            # No more requests, jump out the loop and kill the thread
                            print 'thread finished'
                            loop_enabled=False
                    # Forward received data from server to the client
                    elif input_item==send_sock:
                        if chunk_start>0:
                            chunk_end=time.time()
                        Cli_Sock.sendall(reply)
        # Print exception message and its position
        except Exception, e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print exc_type, fname, exc_tb.tb_lineno
        # Close both sockets
        send_sock.close()
        Cli_Sock.close()
    
if __name__ == '__main__':
    if len(sys.argv) <= 1: 
        print 'Usage: \'python proxy.py port\'\n[port : It is the port of the Proxy Server'
        sys.exit(2)
    my_proxy=proxy(port=int(sys.argv[1]))
    my_proxy.listen()
    

    
