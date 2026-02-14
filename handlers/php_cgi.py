"""
Exécution de scripts PHP via CGI
"""

import asyncio
import os
import shlex
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse, parse_qs

async def execute_php_cgi(script_path: str, method: str, query_string: str,
                         headers: Dict[str, str], body: bytes,
                         php_cgi_path: str = "/usr/bin/php-cgi") -> Tuple[bytes, Optional[Dict[str, str]]]:
    """
    Exécute un script PHP via CGI.

    Args:
        script_path: Chemin absolu du script PHP
        method: Méthode HTTP (GET, POST, etc.)
        query_string: Query string (?param=value)
        headers: Headers HTTP
        body: Corps de la requête (bytes)
        php_cgi_path: Chemin vers php-cgi

    Returns:
        Tuple: (contenu_php, headers_extra) ou (b'', None) en cas d'erreur
    """
    try:
        # Construire les variables d'environnement CGI
        env = build_cgi_env(script_path, method, query_string, headers, body)

        # Préparer les données POST (body est déjà en bytes)
        input_data = body if method == 'POST' and body else None

        # Lancer php-cgi
        process = await asyncio.create_subprocess_exec(
            php_cgi_path,
            env=env,
            stdin=asyncio.subprocess.PIPE if input_data else None,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=os.path.dirname(script_path)  # Répertoire du script
        )

        # Envoyer les données POST et récupérer la sortie
        stdout, stderr = await process.communicate(input=input_data)

        # Vérifier le code de retour
        if process.returncode != 0:
            print(f"Erreur PHP (code {process.returncode}): {stderr.decode()}")
            return b'', None

        # Parser la sortie CGI (headers + body)
        content, extra_headers = parse_cgi_output(stdout)

        return content, extra_headers

    except Exception as e:
        print(f"Erreur exécution PHP {script_path}: {e}")
        return b'', None

def build_cgi_env(script_path: str, method: str, query_string: str,
                 headers: Dict[str, str], body: bytes) -> Dict[str, str]:
    """
    Construit l'environnement CGI pour PHP.

    Args:
        script_path: Chemin du script PHP
        method: Méthode HTTP
        query_string: Query string
        headers: Headers HTTP
        body: Corps de la requête (bytes)

    Returns:
        Dict: Variables d'environnement
    """
    # Variables de base
    env = {
        'REQUEST_METHOD': method,
        'SCRIPT_FILENAME': script_path,
        'SCRIPT_NAME': os.path.basename(script_path),
        'PATH_INFO': '',  # TODO: Support pour PATH_INFO
        'QUERY_STRING': query_string,
        'CONTENT_LENGTH': str(len(body)) if body else '0',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '4610',
        'GATEWAY_INTERFACE': 'CGI/1.1',
        'REDIRECT_STATUS': '200',  # Nécessaire pour PHP
    }

    # Content-Type
    if 'content-type' in headers:
        env['CONTENT_TYPE'] = headers['content-type']

    # Headers HTTP -> variables CGI
    for header_name, header_value in headers.items():
        cgi_name = f"HTTP_{header_name.upper().replace('-', '_')}"
        env[cgi_name] = header_value

    # Variables d'environnement système
    env.update({
        'PATH': os.environ.get('PATH', ''),
        'HOME': os.environ.get('HOME', ''),
        'USER': os.environ.get('USER', ''),
    })

    return env

def parse_cgi_output(output: bytes) -> Tuple[bytes, Optional[Dict[str, str]]]:
    """
    Parse la sortie CGI (headers + body).

    Args:
        output: Sortie brute de php-cgi

    Returns:
        Tuple: (body, headers_dict)
    """
    try:
        text = output.decode('utf-8', errors='ignore')

        # Séparer headers et body
        if '\r\n\r\n' in text:
            header_part, body = text.split('\r\n\r\n', 1)
        else:
            return output, None  # Pas de headers, tout est body

        headers = {}
        for line in header_part.split('\r\n'):
            if ': ' in line:
                key, value = line.split(': ', 1)
                headers[key.lower()] = value
        
        return body.encode('utf-8'), headers

    except Exception as e:
        print(f"Erreur parsing CGI output: {e}")
        return output, None
