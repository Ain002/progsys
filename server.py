#!/usr/bin/env python3
"""
Serveur HTTP avec support PHP
Point d'entrée principal du serveur
"""

import asyncio
import json
import logging
import os
import sys
from typing import Tuple, Dict, Optional
from urllib.parse import urlparse

# Importer les modules du projet
from utils.http_parser import parse_http_request, build_http_response
from handlers.static import handle_static_file
from handlers.php_cgi import execute_php_cgi
from handlers.redirect import get_redirect_location, build_redirect_response

# Configuration globale
CONFIG = {}

def load_config(config_path: str = "config.json") -> Dict:
    """
    Charge la configuration depuis le fichier JSON.

    Args:
        config_path: Chemin vers le fichier de config

    Returns:
        Dict: Configuration chargée
    """
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)

        # Valider la config
        required_keys = ['host', 'port', 'document_root']
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Clé requise manquante: {key}")

        # Chemins absolus
        config['document_root'] = os.path.abspath(config['document_root'])

        return config
    except Exception as e:
        print(f"Erreur chargement config: {e}")
        sys.exit(1)

# ...existing code...
def resolve_path(path: str, document_root: str) -> str:
    # Éviter les chemins avec .. ou absolus (sauf racine)
    if '..' in path:
        return ''

    # Pour la racine, mapper à document_root
    if path == '/':
        return document_root

    # Construire le chemin absolu
    full_path = os.path.join(document_root, path.lstrip('/'))

    # Vérifier que le chemin est dans document_root
    if not os.path.abspath(full_path).startswith(os.path.abspath(document_root)):
        return ''

    return full_path
# ...existing code...

async def handle_request(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    """
    Gère une requête HTTP entrante.

    Args:
        reader: StreamReader pour lire la requête
        writer: StreamWriter pour envoyer la réponse
    """
    addr = writer.get_extra_info('peername')
    print(f"Connexion de {addr}")

    try:
        # Lire la requête complète jusqu'aux headers
        data = b''
        while not data.endswith(b'\r\n\r\n'):
            chunk = await reader.read(1024)
            if not chunk:
                break
            data += chunk
            if len(data) > 8192:
                response = build_http_response(400, "Bad Request")
                writer.write(response)
                await writer.drain()
                return

        if not data:
            return

        # Parser la requête
# ...existing code...
        try:
            method, path, version, headers, body = parse_http_request(data)
            print(f"Requête: {method} {path}")
        except ValueError as e:
            print(f"Requête malformée: {e}")
            print(f"Données brutes: {data[:500]}")  # Log les premiers 500 octets
            response = build_http_response(400, "Bad Request")
# ...existing code...

        # Parser l'URL
        parsed_url = urlparse(path)
        path_only = parsed_url.path
        query_string = parsed_url.query

        # Vérifier les redirections
        redirect_info = get_redirect_location(path_only, CONFIG.get('redirects', {}))
        if redirect_info:
            location, permanent = redirect_info
            response = build_redirect_response(location, permanent)
            writer.write(response)
            await writer.drain()
            return

        # Résoudre le chemin du fichier
        file_path = resolve_path(path_only, CONFIG['document_root'])

        if not file_path:
            # Chemin invalide
            response = build_http_response(400, "Bad Request")
            writer.write(response)
            await writer.drain()
            return

        # Vérifier si c'est un répertoire
        if os.path.isdir(file_path):
            # Chercher index files (redirige direct ao @index.html sinon)
            index_files = CONFIG.get('index_files', ['index.html'])
            found_index = None
            for index_file in index_files:
                index_path = os.path.join(file_path, index_file)
                if os.path.isfile(index_path):
                    found_index = index_path
                    break

            if found_index:
                file_path = found_index
            else:
                # Générer listing répertoire (simple)
                files = os.listdir(file_path)
                html = f"<html><body><h1>Directory: {path_only}</h1><ul>"
                for f in files:
                    html += f'<li><a href="{path_only}/{f}">{f}</a></li>'
                html += "</ul></body></html>"
                response = build_http_response(200, html, "text/html")
                writer.write(response)
                await writer.drain()
                return

        # Vérifier si le fichier existe
        if not os.path.exists(file_path):
            response = build_http_response(404, "Not Found")
            writer.write(response)
            await writer.drain()
            return

        # Traiter selon le type de fichier
        if file_path.endswith('.php') and CONFIG.get('enable_php', True):
            # Exécuter PHP
            content, extra_headers = await execute_php_cgi(
                file_path, method, query_string, headers, body,
                CONFIG.get('php_cgi_path', '/usr/bin/php-cgi')
            )

            if content:
                # Utiliser les headers de PHP si présents
                content_type = "text/html"
                response_headers = {}
                if extra_headers:
                    if 'content-type' in extra_headers:
                        content_type = extra_headers['content-type']
                    response_headers.update(extra_headers)

                # PHP retourne des bytes
                status_line = "HTTP/1.1 200 OK\r\n"
                headers_str = f"Content-Type: {content_type}\r\n"
                headers_str += f"Content-Length: {len(content)}\r\n"
                headers_str += "Connection: close\r\n"
                for key, value in response_headers.items():
                    if key.lower() not in ['content-type', 'content-length', 'connection']:
                        headers_str += f"{key}: {value}\r\n"
                headers_str += "\r\n"
                response = (status_line + headers_str).encode() + content
            else:
                response = build_http_response(500, "Internal Server Error")

        else:
            # Fichier statique
            content, extra_headers = await handle_static_file(
                file_path, headers.get('if-none-match')
            )

            if content is None:
                # 404
                response = build_http_response(404, "Not Found")
            elif not content:
                # 304 Not Modified
                response = build_http_response(304, "", extra_headers=extra_headers)
            else:
                # Contenu avec headers de cache - gérer binaire vs texte
                if isinstance(content, bytes):
                    # Fichier binaire - construire réponse manuellement
                    status_line = "HTTP/1.1 200 OK\r\n"
                    headers_str = f"Content-Type: {extra_headers.get('Content-Type', 'application/octet-stream')}\r\n"
                    headers_str += f"Content-Length: {len(content)}\r\n"
                    if 'ETag' in extra_headers:
                        headers_str += f"ETag: {extra_headers['ETag']}\r\n"
                    if 'Cache-Control' in extra_headers:
                        headers_str += f"Cache-Control: {extra_headers['Cache-Control']}\r\n"
                    headers_str += "Connection: close\r\n\r\n"
                    response = (status_line + headers_str).encode() + content
                else:
                    # Contenu texte
                    response = build_http_response(200, content, extra_headers=extra_headers)

        # Envoyer la réponse
        writer.write(response)
        await writer.drain()

    except Exception as e:
        print(f"Erreur traitement requête: {e}")
        try:
            response = build_http_response(500, "Internal Server Error")
            writer.write(response)
            await writer.drain()
        except:
            pass
    finally:
        writer.close()
        await writer.wait_closed()

async def main():
    """Fonction principale du serveur."""
    global CONFIG
    CONFIG = load_config()

    host = CONFIG['host']
    port = CONFIG['port']

    print(f"Démarrage du serveur HTTP sur {host}:{port}")
    print(f"Document root: {CONFIG['document_root']}")
    print(f"PHP activé: {CONFIG.get('enable_php', True)}")

    server = await asyncio.start_server(handle_request, host, port)

    async with server:
        print("Serveur prêt. Ctrl+C pour arrêter.")
        try:
            await server.serve_forever()
        except KeyboardInterrupt:
            print("Arrêt du serveur...")

if __name__ == "__main__":
    asyncio.run(main())
