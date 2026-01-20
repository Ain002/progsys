import socket

HOST= "192.168.43.229"
PORT= 4608

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b"Jsuis un client")
    data = s.recv(1024)

    print (f"{data} recu")
    