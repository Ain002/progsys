import socket

HOST = "127.0.0.1"
PORT = 4608

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()

    with conn:
        print(f"Connecté par {addr}")
        
        # LIRE la requête du client
        request_data = conn.recv(4096).decode()  # 4KB max pour une requête simple
        print("=== REQUÊTE REÇUE ===")
        print(request_data)
        print("=====================")
        
        # Parser la requête
        # Une requête HTTP ressemble à :
        # GET /chemin HTTP/1.1
        # Host: localhost:4608
        # User-Agent: curl/...
        # 
        # (corps pour POST)
        
        lines = request_data.split('\r\n')
        
        # Première ligne : GET / HTTP/1.1
        request_line = lines[0]
        method, path, http_version = request_line.split()
        
        print(f"Méthode: {method}")
        print(f"Chemin: {path}")
        print(f"Version: {http_version}")
        
        # Headers (lignes jusqu'à la première vide)
        headers = {}
        for line in lines[1:]:
            if not line:  # Ligne vide = fin des headers
                break
            key, value = line.split(': ', 1)
            headers[key] = value
        
        # Corps (body) - pour POST
        body = ""
        if method == "POST":
            # Trouver où commence le corps
            empty_line_index = request_data.find('\r\n\r\n')
            if empty_line_index != -1:
                body = request_data[empty_line_index + 4:]  # +4 pour sauter \r\n\r\n
        
        # Maintenant répondre selon la méthode
        if method == "GET":
            response_body = f"Tu as fait un GET sur {path}"
        elif method == "POST":
            response_body = f"Tu as fait un POST avec corps: {body}"
        else:
            response_body = f"Méthode {method} non supportée"
        
        # Construire la réponse HTTP
        response = (
            f"HTTP/1.1 200 OK\r\n"
            f"Content-Type: text/plain\r\n"
            f"Content-Length: {len(response_body)}\r\n"
            f"\r\n"
            f"{response_body}"
        )
        
        conn.sendall(response.encode())