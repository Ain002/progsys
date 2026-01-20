import socket

HOST= "192.168.43.229"
PORT= 4608

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    conn, addr= s.accept()

    with conn:
        print (f"Connect by {addr}")
        while True:
            data= conn.recv(1024)
            response = (
            "HTTP/1.1 200 OK\n"
            "Content-Type: text/plain\n"
            f"Content-Length: {len(data)}\n"
            "\n"
            f"{data}"
            )
            
            if not data:
                break
            conn.sendall(response)