"""
Détection des types MIME
"""

import os
from typing import Optional

MIME_TYPES = {
    '.html': 'text/html',
    '.htm': 'text/html',
    '.css': 'text/css',
    '.js': 'application/javascript',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
    '.ico': 'image/x-icon',
    '.pdf': 'application/pdf',
    '.txt': 'text/plain',
    '.xml': 'application/xml',
    '.zip': 'application/zip',
    '.php': 'text/html',  # PHP génère généralement du HTML
}

def get_mime_type(filename: str) -> str:
    """
    Retourne le type MIME basé sur l'extension du fichier.

    Args:
        filename: Nom du fichier

    Returns:
        str: Type MIME, 'application/octet-stream' par défaut
    """
    _, ext = os.path.splitext(filename.lower())
    return MIME_TYPES.get(ext, 'application/octet-stream')
  