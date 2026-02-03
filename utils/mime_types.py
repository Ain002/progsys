"""
Détection des types MIME
"""

MIME_TYPES = {
    '.html': 'text/html',
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
}

def get_mime_type(filename):
    """
    Retourne le type MIME basé sur l'extension du fichier
    
    Args:
        filename: Le nom du fichier ou son chemin
        
    Returns:
        str: Le type MIME correspondant ou 'application/octet-stream' par défaut
    """
    import os
    
    # Extraire l'extension du fichier
    _, ext = os.path.splitext(filename.lower())
    
    # Retourner le type MIME correspondant ou par défaut
    return MIME_TYPES.get(ext, 'application/octet-stream')
