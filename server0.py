import socket

'''
Implementation with IPv4/TCP
Process only once and then exit
'''

PORT = 50000

# Create a socket
server_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Binding names to sockets
server_.bind(("", PORT))

# Standby for connection
server_.listen()

# Client processing
client_, addr = server_.accept()
client_.sendall(b'Hi, nice to meat you!\n')
client_.close()
server_.close()
