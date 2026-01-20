import sys
import socket
import selectors
import types

sel = selectors.DefaultSelector()

host = "127.0.0.1" 
port = 4610

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
lsock.bind((host, port))
lsock.listen()
lsock.setblocking(False)

sel.register(lsock, selectors.EVENT_READ, data=None)

print(f"HTTP server listening on {host}:{port}")

def accept_wrapper(sock):
    conn, addr = sock.accept()
    conn.setblocking(False)
    data = types.SimpleNamespace(
        addr=addr,
        inb=b"",
        outb=b"",
        request_done=False
    )
    sel.register(conn, selectors.EVENT_READ | selectors.EVENT_WRITE, data=data)

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data

    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(4096)
        if recv_data:
            data.inb += recv_data

            # Fin des headers HTTP
            if b"\r\n\r\n" in data.inb and not data.request_done:
                data.request_done = True

                request_line = data.inb.split(b"\r\n", 1)[0].decode()
                method, path, version = request_line.split()

                body = f"Hello from HTTP server\nPath: {path}\n".encode()

                response = (
                    b"HTTP/1.1 200 OK\r\n"
                    b"Content-Type: text/plain\r\n"
                    b"Content-Length: " + str(len(body)).encode() + b"\r\n"
                    b"Connection: close\r\n"
                    b"\r\n" +
                    body
                )

                data.outb = response
        else:
            sel.unregister(sock)
            sock.close()

    if mask & selectors.EVENT_WRITE:
        if data.outb:
            sent = sock.send(data.outb)
            data.outb = data.outb[sent:]
        else:
            sel.unregister(sock)
            sock.close()

try:
    while True:
        events = sel.select()
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)
except KeyboardInterrupt:
    print("Server stopped")
finally:
    sel.close()
