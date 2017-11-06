import socket
import sys
if len(sys.argv) <= 1: 
    print 'Usage: "python S.py port"\n[port : It is the port of the Proxy Server'
    sys.exit(2)

# Server socket created, bound and starting to listen
Serv_Port = int(sys.argv[1]) # sys.argv[1] is the port number entered by the user
Serv_Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # socket.socket function creates a socket.

# Prepare a server socket
print "starting server ...."
Serv_Sock.bind(('', Serv_Port))
Serv_Sock.listen(5)


def browse(splitMessage, Cli_Sock):
    #this method is responsible for caching
    Req_Type = splitMessage[0]
    Req_path = splitMessage[1]
    Req_path = Req_path[1:]
    print "Request is ", Req_Type, " to URL : ", Req_path
    serv_proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host_name = Req_path
    print "HOST NAME:", host_name
    host_ip = socket.gethostbyname(host_name)
    print "HOST IP:", host_ip
    try:
        serv_proxy.connect((host_ip, 80))
        print 'Socket connected to port 80 of the host'
    except:
        print 'Illegal Request'
    Cli_Sock.close()
# while True:
if __name__ == '__main__':
    # Start receiving data from the client
    print 'Initiating server... \nAccepting connection\n'
    Cli_Sock, addr = Serv_Sock.accept() # Accept a connection from client
    # print addr

    print ' connection received from: ', addr
    message = Cli_Sock.recv(1024) #Recieves data from Socket

    splitMessage = message.split()

    browse(splitMessage, Cli_Sock)