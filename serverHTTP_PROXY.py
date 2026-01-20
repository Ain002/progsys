import socket
import selectors
import types
from urllib.parse import urlparse

HOST = "127.0.0.1"
PORT = 4610

sel = selectors.DefaultSelector()

def accept(sock):
    conn, addr = sock.accept()
    conn.setblocking(False)
    data = types.SimpleNamespace(
        client=conn,
        remote=None,
        inb=b"",
        outb=b"",
        stage="READ_CLIENT"
    )
    sel.register(conn, selectors.EVENT_READ, data)

def connect_remote(data, method, url, version, headers, raw_request):
    parsed = urlparse(url)

    host = parsed.hostname
    port = parsed.port or 80
    path = parsed.path or "/"
    if parsed.query:
        path += "?" + parsed.query

    # Rebuild request (proxy → server : path relatif)
    request_line = f"{method} {path} {version}\r\n"
    header_lines = ""

    for k, v in headers.items():
        if k.lower() != "proxy-connection":
            header_lines += f"{k}: {v}\r\n"

    forward = (request_line + header_lines + "\r\n").encode()

    remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote.setblocking(False)
    remote.connect_ex((host, port))

    data.remote = remote
    data.outb = forward
    data.stage = "CONNECT_REMOTE"

    sel.register(remote, selectors.EVENT_WRITE, data)

def service(key, mask):
    sock = key.fileobj
    data = key.data

    # ===== CLIENT → PROXY =====
    if sock == data.client and mask & selectors.EVENT_READ:
        chunk = sock.recv(4096)
        if not chunk:
            close(data)
            return

        data.inb += chunk

        if b"\r\n\r\n" in data.inb:
            try:
                text = data.inb.decode()
                header, _, body = text.partition("\r\n\r\n")
                lines = header.split("\r\n")
                method, url, version = lines[0].split()

                headers = {}
                for line in lines[1:]:
                    if ": " in line:
                        k, v = line.split(": ", 1)
                        headers[k] = v

                connect_remote(data, method, url, version, headers, data.inb)

                sel.modify(data.client, 0, data)

            except Exception:
                close(data)

    # ===== PROXY → SERVER =====
    if data.remote and sock == data.remote and mask & selectors.EVENT_WRITE:
        sent = sock.send(data.outb)
        data.outb = data.outb[sent:]
        if not data.outb:
            sel.modify(sock, selectors.EVENT_READ, data)

    # ===== SERVER → PROXY =====
    if data.remote and sock == data.remote and mask & selectors.EVENT_READ:
        resp = sock.recv(4096)
        if resp:
            data.outb += resp
            sel.modify(data.client, selectors.EVENT_WRITE, data)
        else:
            sel.unregister(sock)
            sock.close()

    # ===== PROXY → CLIENT =====
    if sock == data.client and mask & selectors.EVENT_WRITE:
        sent = sock.send(data.outb)
        data.outb = data.outb[sent:]
        if not data.outb:
            close(data)

def close(data):
    for s in (data.client, data.remote):
        if s:
            try:
                sel.unregister(s)
            except Exception:
                pass
            s.close()

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
lsock.bind((HOST, PORT))
lsock.listen()
lsock.setblocking(False)

sel.register(lsock, selectors.EVENT_READ, data=None)

print(f"HTTP Proxy listening on {HOST}:{PORT}")

while True:
    for key, mask in sel.select():
        if key.data is None:
            accept(key.fileobj)
        else:
            service(key, mask)
