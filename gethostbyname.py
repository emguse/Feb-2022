import socket

try:
    hostname = input("Server to connect to : ")
    print(socket.gethostbyname(hostname))
except:
    print("Could not convert")