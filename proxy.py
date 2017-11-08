import socket
import sys
import select


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


def browse(Cli_Sock):
    global BUFF_SIZE
    num=1
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # send_sock.bind(('',8080))
        send_sock.settimeout(0.30)
        send_sock.connect(('3.0.0.1',80))
        # message = (
        #     'GET / HTTP/1.0\r\n'
        #     'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0\r\n'
        #     'Connection: keep-alive\r\n\r\n'
        #     )
        # input_list=[Cli_Sock,send_sock]
        length=1
        while length:
            inputready, output_ready, exceptready = select.select([Cli_Sock],[Cli_Sock],[])
            for input_item in inputready:
                reply = input_item.recv(BUFF_SIZE)
                length=len(reply)
                if input_item==Cli_Sock:
                    send_sock.sendall(reply)
                    # print 'client data:%s'%reply
                else:
                    Cli_Sock.sendall(reply)
                    # print '###CLIENT###'
            # print '%dth attempt SUCCESSEDED\n'%num
            # num+=1
        
    except Exception, e:
        print e
        print '%dth attempt FAILED\n'%num
def main():
    try:
        while True:
            # Start receiving data from the client
            print 'Initiating server... \nAccepting connection\n'
            Cli_Sock, Cli_addr = Serv_Sock.accept() # Accept a connection from client
            # print addr
            print 'Connection received from: ', Cli_addr
            # message = Cli_Sock.recv(1024)

            # splitMessage = message.split()
            # print message
            browse(Cli_Sock)
            Cli_Sock.close()
            
    except KeyboardInterrupt:
        print 'Closing server...'
        Serv_Sock.close()
        sys.exit()
if __name__ == '__main__':
    BUFF_SIZE=1024
    main()
    

    