"""
Parser HTTP pour requêtes et réponses
"""

import urllib.parse
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
