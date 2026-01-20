import socket

HOST = "127.0.0.1"
PORT = 4608

def parse_http_request(data: str):
    header_part, _, body = data.partition("\r\n\r\n")
    lines = header_part.split("\r\n")

    method, path, version = lines[0].split()

    headers = {}
    for line in lines[1:]:
        key, value = line.split(": ", 1)
        headers[key] = value

    return method, path, version, headers, body


def build_http_response(status_code: int, body: str, content_type="text/plain"):
    reason = {
        200: "OK",
        400: "Bad Request",
        404: "Not Found",
        405: "Method Not Allowed",
    }.get(status_code, "OK")

    response = (
        f"HTTP/1.1 {status_code} {reason}\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(body.encode())}\r\n"
        f"Connection: close\r\n"
        f"\r\n"
        f"{body}"
    )
    return response.encode()


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()

    while True:
        conn, addr = server.accept()
        with conn:
            data = conn.recv(8192)
            if not data:
                continue

            try:
                request_text = data.decode()
                print("REQUETE RECU")
                print(request_text)
                
                method, path, version, headers, body = parse_http_request(request_text)
                
                if method == "GET":
                    response_body = f"GET {path}"
                    response = build_http_response(200, response_body)

                elif method == "POST":
                    response_body = f"POST {path}\n{body}"
                    response = build_http_response(200, response_body)

                else:
                    response = build_http_response(405, "Method Not Allowed")

            except Exception:
                response = build_http_response(400, "Bad Request")

            conn.sendall(response)
