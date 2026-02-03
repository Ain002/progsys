"""
Gestionnaire de fichiers statiques
"""

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
