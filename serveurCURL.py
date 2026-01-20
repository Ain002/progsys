import socket

HOST= "127.0.0.1"
PORT= 4608

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    conn, addr= s.accept()

    with conn:
        print (f"Connect by {addr}")
        body = "Hello HTTP"
        response = (
            "HTTP/1.1 200 OK\n"
            "Content-Type: text/plain\n"
            f"Content-Length: {len(body)}\n"
            "\n"
            f"{body}"
        )
        print (f"{response}")
        conn.sendall(response.encode())
        