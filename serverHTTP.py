import socket
import selectors
import types

HOST = "127.0.0.1"
PORT = 4610

sel = selectors.DefaultSelector()

def parse_http_request(data: bytes):
    text = data.decode()
    header_part, _, body = text.partition("\r\n\r\n")
    lines = header_part.split("\r\n")

    method, path, version = lines[0].split()

    headers = {}
    for line in lines[1:]:
        if ": " in line:
            k, v = line.split(": ", 1)
            headers[k] = v

    return method, path, version, headers, body

def build_http_response(code, body, content_type="text/plain"):
    reason = {
        200: "OK",
        400: "Bad Request",
        404: "Not Found",
        405: "Method Not Allowed"
    }.get(code, "OK")

    body_bytes = body.encode()

    response = (
        f"HTTP/1.1 {code} {reason}\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(body_bytes)}\r\n"
        f"Connection: close\r\n"
        f"\r\n"
    ).encode() + body_bytes

    return response

def accept(sock):
    conn, addr = sock.accept()
    conn.setblocking(False)
    data = types.SimpleNamespace(
        addr=addr,
        inb=b"",
        outb=b"",
        request_done=False
    )
    sel.register(conn, selectors.EVENT_READ | selectors.EVENT_WRITE, data)

def service(key, mask):
    sock = key.fileobj
    data = key.data

    if mask & selectors.EVENT_READ:
        chunk = sock.recv(4096)
        if chunk:
            data.inb += chunk
            if b"\r\n\r\n" in data.inb and not data.request_done:
                data.request_done = True

                try:
                    method, path, version, headers, body = parse_http_request(data.inb)

                    if method == "GET":
                        resp = build_http_response(200, f"GET {path}")
                    elif method == "POST":
                        resp = build_http_response(200, f"POST {path}\n{body}")
                    else:
                        resp = build_http_response(405, "Method Not Allowed")
                except Exception:
                    resp = build_http_response(400, "Bad Request")

                data.outb = resp
        else:
            sel.unregister(sock)
            sock.close()

    if mask & selectors.EVENT_WRITE and data.outb:
        sent = sock.send(data.outb)
        data.outb = data.outb[sent:]
        if not data.outb:
            sel.unregister(sock)
            sock.close()

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
lsock.bind((HOST, PORT))
lsock.listen()
lsock.setblocking(False)

sel.register(lsock, selectors.EVENT_READ, data=None)

print(f"HTTP server listening on {HOST}:{PORT}")

while True:
    for key, mask in sel.select():
        if key.data is None:
            accept(key.fileobj)
        else:
            service(key, mask)
