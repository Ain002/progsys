#!/usr/bin/env python3
"""
Serveur HTTP avec support PHP
Point d'entrée principal du serveur
Gère les requêtes HTTP, le cache, les réponses avec ETags et la compression gzip
"""

import asyncio
import hashlib
import gzip
import gzip

# Importer le cache LRU pour la gestion du cache de fichiers statiques
from handlers.cache import LRUCache

# TODO: Implémenter le serveur asyncio avec support complet HTTP/1.1

# Cache global pour les fichiers statiques
# Capacité limitée à 200 fichiers pour éviter une consommation mémoire excessive
static_cache = LRUCache(capacity=200)


def compute_etag(content):
    """
    Calcule un ETag (Entity Tag) pour un contenu donné.
    Utilise MD5 pour générer un identifiant unique du contenu.
    
    Args:
        content: Le contenu (bytes) pour lequel générer l'ETag
        
    Returns:
        String hexadécimal représentant l'ETag
    """
    return hashlib.md5(content).hexdigest()


def gzip_compress(data):
    """
    Compresse les données en utilisant l'algorithme gzip.
    Utilisé pour réduire la taille des réponses.
    
    Args:
        data: Les données (bytes) à compresser
        
    Returns:
        Les données compressées en bytes
    """
    return gzip.compress(data, compresslevel=9)


def should_compress(mime_type):
    """
    Vérifie si le type MIME doit être compressé.
    Seuls HTML, CSS et JS sont compressés (texte bénéficiant de la compression).
    
    Args:
        mime_type: Le type MIME du contenu
        
    Returns:
        True si le contenu doit être compressé, False sinon
    """
    compressible_types = {
        "text/html",
        "text/css",
        "application/javascript",
        "text/javascript"
    }
    return mime_type in compressible_types


def compute_etag(content):
    """
    Calcule un ETag (Entity Tag) pour un contenu donné.
    Utilise MD5 pour générer un identifiant unique du contenu.
    
    Args:
        content: Le contenu (bytes) pour lequel générer l'ETag
        
    Returns:
        String hexadécimal représentant l'ETag
    """
    return hashlib.md5(content).hexdigest()


def gzip_compress(data):
    """
    Compresse les données en utilisant l'algorithme gzip.
    Utilisé pour réduire la taille des réponses.
    
    Args:
        data: Les données (bytes) à compresser
        
    Returns:
        Les données compressées en bytes
    """
    return gzip.compress(data, compresslevel=9)


def should_compress(mime_type):
    """
    Vérifie si le type MIME doit être compressé.
    Seuls HTML, CSS et JS sont compressés (texte bénéficiant de la compression).
    
    Args:
        mime_type: Le type MIME du contenu
        
    Returns:
        True si le contenu doit être compressé, False sinon
    """
    compressible_types = {
        "text/html",
        "text/css",
        "application/javascript",
        "text/javascript"
    }
    return mime_type in compressible_types


def handle_etag_validation(content, request_headers, headers):
    """
    Valide l'ETag de la réponse avec la requête client.
    Retourne une réponse 304 Not Modified si le contenu n'a pas changé.
    
    Args:
        content: Le contenu à valider
        request_headers: Les headers de la requête HTTP
        headers: Les headers de la réponse
        
    Returns:
        Tuple (status_code, headers, response_body) ou None si validation OK
    """
    # Générer l'ETag du contenu actuel
    etag = compute_etag(content)
    headers["ETag"] = etag
    
    # Récupérer l'ETag envoyé par le client dans "If-None-Match"
    client_etag = request_headers.get("If-None-Match")

    # Si l'ETag correspond, retourner 304 Not Modified
    if client_etag == etag:
        return 304, {"ETag": etag}, b""
    
    return None


if __name__ == "__main__":
    print("Serveur HTTP - En développement")

import json
import logging
import os
import sys
import time
from typing import Tuple, Dict, Optional
from urllib.parse import urlparse


# Importer les modules du projet
from utils.http_parser import parse_http_request, build_http_response
from handlers.static import handle_static_file
from handlers.php_cgi import execute_php_cgi
from handlers.redirect import get_redirect_location, build_redirect_response
from handlers.monitoring import monitor, generate_monitoring_dashboard
from handlers.monitoring_widget import inject_monitoring_widget

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

async def handle_request(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    """
    Gère une requête HTTP entrante.

    Args:
        reader: StreamReader pour lire la requête
        writer: StreamWriter pour envoyer la réponse
    """
    addr = writer.get_extra_info('peername')
    client_ip = addr[0] if addr else 'unknown'
    print(f"Connexion de {addr}")
    
    # Timer pour mesurer la latence
    start_time = time.time()
    status_code = 200
    method = 'UNKNOWN'
    path = '/'

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
                status_code = 400
                monitor.record_request(method, path, status_code, time.time() - start_time, client_ip)
                return

        if not data:
            return

        # Parser la requête
        try:
            method, path, version, headers, body = parse_http_request(data)
            print(f"Requête: {method} {path}")
        except ValueError as e:
            print(f"Requête malformée: {e}")
            print(f"Données brutes: {data[:500]}")  # Log les premiers 500 octets
            response = build_http_response(400, "Bad Request")
            writer.write(response)
            await writer.drain()
            status_code = 400
            monitor.record_request(method, path, status_code, time.time() - start_time, client_ip)
            return

        # Parser l'URL
        parsed_url = urlparse(path)
        path_only = parsed_url.path
        query_string = parsed_url.query
        
        # Endpoint spécial pour le monitoring
        if path_only == '/_monitor' or path_only == '/_monitoring':
            # Mettre à jour les stats du cache
            from handlers.static import file_cache
            monitor.update_cache_stats(file_cache.get_stats())
            
            # Générer le dashboard
            stats = monitor.get_stats()
            html_content = generate_monitoring_dashboard(stats)
            
            status_line = "HTTP/1.1 200 OK\r\n"
            headers_str = "Content-Type: text/html; charset=utf-8\r\n"
            headers_str += f"Content-Length: {len(html_content)}\r\n"
            headers_str += "Connection: close\r\n\r\n"
            response = (status_line + headers_str).encode() + html_content
            
            writer.write(response)
            await writer.drain()
            status_code = 200
            monitor.record_request(method, path_only, status_code, time.time() - start_time, client_ip)
            return
        
        # API JSON pour le widget
        if path_only == '/_monitor/api':
            from handlers.cache import cache
            monitor.update_cache_stats(cache.get_stats())
            
            stats = monitor.get_stats()
            json_content = json.dumps(stats).encode('utf-8')
            
            status_line = "HTTP/1.1 200 OK\r\n"
            headers_str = "Content-Type: application/json\r\n"
            headers_str += f"Content-Length: {len(json_content)}\r\n"
            headers_str += "Connection: close\r\n\r\n"
            response = (status_line + headers_str).encode() + json_content
            
            writer.write(response)
            await writer.drain()
            status_code = 200
            monitor.record_request(method, path_only, status_code, time.time() - start_time, client_ip)
            return

        # Vérifier les redirections
        redirect_info = get_redirect_location(path_only, CONFIG.get('redirects', {}))
        if redirect_info:
            location, permanent = redirect_info
            response = build_redirect_response(location, permanent)
            status_code = 301 if permanent else 302
            writer.write(response)
            await writer.drain()
            monitor.record_request(method, path_only, status_code, time.time() - start_time, client_ip)
            return

        # Résoudre le chemin du fichier
        file_path = resolve_path(path_only, CONFIG['document_root'])

        if not file_path:
            # Chemin invalide
            response = build_http_response(400, "Bad Request")
            writer.write(response)
            await writer.drain()
            status_code = 400
            monitor.record_request(method, path_only, status_code, time.time() - start_time, client_ip)
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
                # Générer listing répertoire (joli)
                from handlers.directory_listing import generate_directory_listing
                html_content = generate_directory_listing(file_path, path_only, CONFIG['document_root'])
                
                # Injecter le widget
                html_content = inject_monitoring_widget(html_content)
                
                status_line = "HTTP/1.1 200 OK\r\n"
                headers_str = "Content-Type: text/html; charset=utf-8\r\n"
                headers_str += f"Content-Length: {len(html_content)}\r\n"
                headers_str += "Connection: close\r\n\r\n"
                response = (status_line + headers_str).encode() + html_content
                
                writer.write(response)
                await writer.drain()
                status_code = 200
                monitor.record_request(method, path_only, status_code, time.time() - start_time, client_ip)
                return

        # Vérifier si le fichier existe
        if not os.path.exists(file_path):
            response = build_http_response(404, "Not Found")
            writer.write(response)
            await writer.drain()
            status_code = 404
            monitor.record_request(method, path_only, status_code, time.time() - start_time, client_ip)
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
                
                # Injecter le widget si HTML
                if 'text/html' in content_type:
                    content = inject_monitoring_widget(content)
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
                status_code = 500

        else:
            # Fichier statique
            content, extra_headers = await handle_static_file(
                file_path, headers.get('if-none-match')
            )

            if content is None:
                # 404
                response = build_http_response(404, "Not Found")
                status_code = 404
            elif not content:
                # 304 Not Modified
                response = build_http_response(304, "", extra_headers=extra_headers)
                status_code = 304
            else:
                # Contenu avec headers de cache - gérer binaire vs texte
                if isinstance(content, bytes):
                    # Injecter le widget si c'est du HTML
                    content_type = extra_headers.get('Content-Type', 'application/octet-stream')
                    if 'text/html' in content_type:
                        content = inject_monitoring_widget(content)
                    
                    # Fichier binaire - construire réponse manuellement
                    status_line = "HTTP/1.1 200 OK\r\n"
                    headers_str = f"Content-Type: {content_type}\r\n"
                    headers_str += f"Content-Length: {len(content)}\r\n"
                    if 'ETag' in extra_headers:
                        headers_str += f"ETag: {extra_headers['ETag']}\r\n"
                    if 'Cache-Control' in extra_headers:
                        headers_str += f"Cache-Control: {extra_headers['Cache-Control']}\r\n"
                    headers_str += "Connection: close\r\n\r\n"
                    response = (status_line + headers_str).encode() + content
                    status_code = 200
                else:
                    # Contenu texte
                    response = build_http_response(200, content, extra_headers=extra_headers)
                    status_code = 200

        # Envoyer la réponse
        writer.write(response)
        await writer.drain()
        
        # Enregistrer la requête dans le monitoring
        latency = time.time() - start_time
        monitor.record_request(method, path_only, status_code, latency, client_ip)

    except Exception as e:
        print(f"Erreur traitement requête: {e}")
        status_code = 500
        try:
            response = build_http_response(500, "Internal Server Error")
            writer.write(response)
            await writer.drain()
            monitor.record_request(method, path, status_code, time.time() - start_time, client_ip)
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
