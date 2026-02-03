"""
Parser HTTP pour requêtes et réponses
"""

import urllib.parse
from typing import Dict, Optional, Tuple


class HTTPRequest:
    """Représente une requête HTTP parsée"""
    
    def __init__(self):
        self.method = ""
        self.path = ""
        self.query_string = ""
        self.version = "HTTP/1.1"
        self.headers = {}
        self.body = b""
        self.params = {}
    
    def get_path_info(self):
        """Retourne le path sans query string"""
        return self.path.split('?')[0] if '?' in self.path else self.path


def parse_request(raw_request: bytes) -> HTTPRequest:
    """
    Parse une requête HTTP complète
    
    Args:
        raw_request: La requête HTTP brute en bytes
        
    Returns:
        HTTPRequest: L'objet requête parsé
    """
    request = HTTPRequest()
    
    try:
        # Convertir en string et séparer headers/body
        request_text = raw_request.decode('utf-8', errors='ignore')
        if '\r\n\r\n' in request_text:
            headers_text, body_text = request_text.split('\r\n\r\n', 1)
            request.body = body_text.encode('utf-8', errors='ignore')
        else:
            headers_text = request_text
            request.body = b""
        
        # Parser la ligne de requête
        lines = headers_text.split('\r\n')
        if lines:
            request_line = lines[0].strip()
            parts = request_line.split(' ')
            if len(parts) >= 3:
                request.method = parts[0].upper()
                full_path = parts[1]
                request.version = parts[2]
                
                # Séparer path et query string
                if '?' in full_path:
                    request.path, request.query_string = full_path.split('?', 1)
                    request.params = urllib.parse.parse_qs(request.query_string)
                else:
                    request.path = full_path
                    request.query_string = ""
                    request.params = {}
        
        # Parser les headers
        for line in lines[1:]:
            if ':' in line:
                key, value = line.split(':', 1)
                request.headers[key.strip().lower()] = value.strip()
    
    except Exception as e:
        # En cas d'erreur, retourner une requête vide
        pass
    
    return request


def parse_headers(headers_text: str) -> Dict[str, str]:
    """
    Parse uniquement les headers HTTP
    
    Args:
        headers_text: Texte des headers
        
    Returns:
        Dict[str, str]: Dictionnaire des headers
    """
    headers = {}
    for line in headers_text.split('\r\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            headers[key.strip().lower()] = value.strip()
    return headers


def extract_method_path_query(request_line: str) -> Tuple[str, str, str]:
    """
    Extrait méthode, path et query string de la ligne de requête
    
    Args:
        request_line: Ligne de requête HTTP (ex: "GET /index.php?user=john HTTP/1.1")
        
    Returns:
        Tuple[str, str, str]: (method, path, query_string)
    """
    parts = request_line.strip().split(' ')
    if len(parts) < 2:
        return "", "", ""
    
    method = parts[0].upper()
    full_path = parts[1]
    
    if '?' in full_path:
        path, query_string = full_path.split('?', 1)
    else:
        path = full_path
        query_string = ""
    
    return method, path, query_string


def get_post_body(request: HTTPRequest) -> Dict[str, str]:
    """
    Extrait les données POST du body
    
    Args:
        request: Objet HTTPRequest
        
    Returns:
        Dict[str, str]: Données POST parsées
    """
    if request.method != 'POST' or not request.body:
        return {}
    
    content_type = request.headers.get('content-type', '').lower()
    
    if content_type == 'application/x-www-form-urlencoded':
        body_text = request.body.decode('utf-8', errors='ignore')
        return urllib.parse.parse_qs(body_text)
    
    # Pour d'autres content-types, retourner le body brut
    return {'raw_body': request.body.decode('utf-8', errors='ignore')}
class HttpRequest:
    def __init__(self, method, path, query, version, headers, body):
        self.method = method
        self.path = path
        self.query = query
        self.version = version
        self.headers = headers
        self.body = body
from typing import Dict, Tuple, Optional

def parse_http_request(data: bytes) -> Tuple[str, str, str, Dict[str, str], str]:
    """
    Parse une requête HTTP brute en bytes.

    Args:
        data: Les données brutes de la requête HTTP

    Returns:
        Tuple: (method, path, version, headers, body)

    Raises:
        ValueError: Si la requête est malformée
    """
    try:
        # Convertir en string
        text = data.decode('utf-8', errors='ignore')

        # Séparer headers et body
        header_part, _, body = text.partition('\r\n\r\n')

        # Parser la ligne de requête
        lines = header_part.split('\r\n')
        if not lines:
            raise ValueError("Requête vide")

        request_line = lines[0]
        parts = request_line.split()
        if len(parts) != 3:
            raise ValueError(f"Ligne de requête invalide: {request_line}")

        method, raw_path, version = parts

        # Décoder l'URL (déchiffrer les URLs)
        path = urllib.parse.unquote(raw_path)

        # Parser les headers
        headers = {}
        for line in lines[1:]:
            if ': ' in line:
                key, value = line.split(': ', 1)
                headers[key.lower()] = value  # Normaliser en minuscules

        return method, path, version, headers, body

    except Exception as e:
        raise ValueError(f"Erreur de parsing HTTP: {e}")

def build_http_response(status_code: int, body: str = "", content_type: str = "text/plain",
                       extra_headers: Optional[Dict[str, str]] = None) -> bytes:
    """
    Construit une réponse HTTP.

    Args:
        status_code: Code de statut HTTP
        body: Corps de la réponse
        content_type: Type de contenu
        extra_headers: Headers supplémentaires

    Returns:
        bytes: Réponse HTTP encodée
    """
    # Codes de statut
    status_messages = {
        200: "OK",
        301: "Moved Permanently",
        302: "Found",
        304: "Not Modified",
        400: "Bad Request",
        404: "Not Found",
        405: "Method Not Allowed",
        500: "Internal Server Error",
    }

    reason = status_messages.get(status_code, "OK")

    # Headers de base
    headers = {
        "Content-Type": content_type,
        "Content-Length": str(len(body.encode('utf-8'))),
        "Connection": "close",
    }

    # Ajouter headers supplémentaires
    if extra_headers:
        headers.update(extra_headers)

    # Construire la réponse
    response_lines = [f"HTTP/1.1 {status_code} {reason}"]
    for key, value in headers.items():
        response_lines.append(f"{key}: {value}")
    response_lines.append("")  # Ligne vide
    response_lines.append(body)

    response = '\r\n'.join(response_lines)
    return response.encode('utf-8')

def parse_query_string(query_string: str) -> Dict[str, str]:
    """
    Parse une query string en dictionnaire.

    Args:
        query_string: La query string (sans le ?)

    Returns:
        Dict: Paramètres décodés
    """
    params = {}
    if query_string:
        for pair in query_string.split('&'):
            if '=' in pair:
                key, value = pair.split('=', 1)
                params[urllib.parse.unquote(key)] = urllib.parse.unquote(value)
            else:
                params[urllib.parse.unquote(pair)] = ""
    return params

def parse_form_data(body: str, content_type: str) -> Dict[str, str]:
    """
    Parse les données de formulaire (application/x-www-form-urlencoded).

    Args:
        body: Corps de la requête
        content_type: Type de contenu

    Returns:
        Dict: Données du formulaire
    """
    if 'application/x-www-form-urlencoded' in content_type:
        return parse_query_string(body)
    return {}
