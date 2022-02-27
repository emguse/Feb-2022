import socket
import datetime

'''
Implementation with IPv4/TCP
Returns the time to the client when a connection request is made
Stop at Ctrl+Break
'''

PORT = 50000
BUFFSIZE = 4096

# Create a socket
server_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Binding names to sockets
server_.bind(("", PORT))

# Standby for connection
server_.listen()

# Client processing
while True:
    client_, addr = server_.accept()
    msg = str(datetime.datetime.now())
    client_.sendall(msg.encode('UTF-8'))
    print(msg, "Connection Requests")
    print(client_)
    data = client_.recv(BUFFSIZE)
    print(data.decode('UTF-8'))

    client_.sendall(msg.encode('UTF-8'))
    client_.close()
