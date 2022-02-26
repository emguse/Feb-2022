import socket
import datetime

'''
Implementation with IPv4/UDP
Process only once and then exit
Stop at Ctrl+Break
'''

PORT = 50000
BUFFSIZE = 4096

# Create a socket
server_ = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Binding names to sockets
server_.bind(("", PORT))

# Client processing
while True:
    data , client = server_.recvfrom(BUFFSIZE)
    msg = str(datetime.datetime.now())
    server_.sendto(msg.encode('UTF-8'), client)
    print(msg, "Connection Requests")
    print(client)
