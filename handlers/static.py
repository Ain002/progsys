"""
Gestionnaire de fichiers statiques
Permet de servir des fichiers statiques (HTML, CSS, JS, images, etc.)
Supporte la compression gzip pour les fichiers texte (HTML, CSS, JS)
"""

import os
import gzip

# TODO: Implémenter la gestion des fichiers statiques

def should_compress(mime_type):
    """
    Vérifie si le type MIME doit être compressé.
    Seuls HTML, CSS et JS sont compressés.
    
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


def handle_static_request(path, static_cache, request_headers=None):
    """
    Traite une requête pour un fichier statique.
    Supporte la compression gzip si le client l'accepte.
    
    Args:
        path: Chemin du fichier statique à servir
        static_cache: Cache pour stocker les fichiers statiques
        request_headers: Headers de la requête HTTP (optionnel)
    
    Returns:
        Tuple (status_code, headers, content)
    """
    if request_headers is None:
        request_headers = {}
    
    # Vérifier si le fichier est en cache
    cached = static_cache.get(path)
    if cached:
        # Retourner le fichier depuis le cache
        content, mime_type, mtime = cached
        return _prepare_response(content, mime_type, request_headers)

    # Lire le fichier depuis le disque
    with open(path, "rb") as f:     
        content = f.read()

    # Déterminer le type MIME du fichier
    mime_type = "text/html"
    
    # Récupérer la date de modification du fichier
    mtime = os.path.getmtime(path)

    # Mettre en cache le fichier
    static_cache.put(path, (content, mime_type, mtime))
    
    # Préparer et retourner la réponse avec compression si nécessaire
    return _prepare_response(content, mime_type, request_headers)


def _prepare_response(content, mime_type, request_headers):
    """
    Prépare la réponse HTTP en appliquant la compression gzip si acceptable.
    
    Args:
        content: Le contenu du fichier
        mime_type: Le type MIME du fichier
        request_headers: Les headers de la requête HTTP
        
    Returns:
        Tuple (status_code, headers, content)
    """
    headers = {
        "Content-Type": mime_type,
        "Cache-Control": "max-age=3600"
    }
    
    # Vérifier si le client accepte gzip et si le contenu est compressible
    accept_encoding = request_headers.get("Accept-Encoding", "")
    if "gzip" in accept_encoding and should_compress(mime_type):
        # Compresser le contenu
        content = gzip.compress(content, compresslevel=9)
        headers["Content-Encoding"] = "gzip"
    
    # Retourner la réponse avec le code 200 OK
    return 200, headers, content

    # Mettre en cache le fichier
    static_cache.put(path, (content, mime_type, mtime))
    
    # Ajouter les headers de cache et retourner le fichier avec le code 200 OK
    headers = {
        "Content-Type": mime_type,
        "Cache-Control": "max-age=3600"
    }
    return 200, headers, content
import asyncio
import os
from typing import Optional, Tuple

from utils.mime_types import get_mime_type
from handlers.cache import cache, generate_etag, should_use_cache

async def handle_static_file(file_path: str, if_none_match: Optional[str] = None) -> Tuple[bytes, Optional[dict]]:
    """
    Sert un fichier statique avec gestion du cache.

    Args:
        file_path: Chemin absolu du fichier
        if_none_match: Header If-None-Match du client

    Returns:
        Tuple: (contenu, headers_extra) ou (b'', headers_304) pour 304
    """
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        return b'', None  # 404

    # Vérifier le cache
    cache_key = file_path
    cached_item = cache.get(cache_key)

    if cached_item:
        content, mime_type, etag, mtime = cached_item

        # Vérifier si le fichier a changé
        if should_use_cache(file_path, mtime):
            # Vérifier ETag
            if if_none_match == etag:
                # 304 Not Modified
                headers_304 = {
                    'ETag': etag,
                    'Cache-Control': 'public, max-age=3600'
                }
                return b'', headers_304

            # Retourner depuis le cache
            headers = {
                'Content-Type': mime_type,
                'ETag': etag,
                'Cache-Control': 'public, max-age=3600'
            }
            return content, headers
        else:
            # Fichier modifié, invalider le cache
            cache.invalidate(cache_key)

    # Lire le fichier
    try:
        with open(file_path, 'rb') as f:
            content = f.read()

        # Détecter le type MIME
        mime_type = get_mime_type(file_path)

        # Générer ETag
        etag = generate_etag(content)

        # Mettre en cache
        mtime = os.path.getmtime(file_path)
        cache.put(cache_key, (content, mime_type, etag, mtime))

        # Headers
        headers = {
            'Content-Type': mime_type,
            'ETag': etag,
            'Cache-Control': 'public, max-age=3600'
        }

        return content, headers

    except (OSError, IOError) as e:
        print(f"Erreur lecture fichier {file_path}: {e}")
        return b'', None
