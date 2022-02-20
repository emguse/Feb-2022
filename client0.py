import socket

'''Implementation with IPv4/TCP'''

HOST = "localhost" # or HOST = "127.0.0.1"
PORT = 50000
BUFFSIZE = 4096

# Create a socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
client.connect((HOST, PORT)) 

# Recieve message
data = client.recv(BUFFSIZE)
print(data.decode('UTF-8'))

# Connection close
client.close()