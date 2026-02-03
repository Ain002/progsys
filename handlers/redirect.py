"""
Gestion des redirections HTTP
"""

# TODO: Implémenter les redirections

def handle_redirect(path, static_cache):
    """
    Gère les redirections HTTP spéciales.
    
    Args:
        path: Le chemin de la requête
        static_cache: Le cache global des fichiers statiques
        
    Returns:
        Tuple (status_code, headers, content) ou None si pas de redirection
    """
    if path == "/admin/cache/clear":
        # Vider le cache et retourner une confirmation
        static_cache.cache.clear()
        return 200, {}, b"Cache cleared"
    
    return None
from typing import Optional, Tuple, Dict

def get_redirect_location(path: str, redirects_config: Dict[str, str]) -> Optional[Tuple[str, bool]]:
    """
    Vérifie si le chemin nécessite une redirection.

    Args:
        path: Chemin demandé
        redirects_config: Configuration des redirections

    Returns:
        Tuple: (location, permanent) ou None si pas de redirection
    """
    # Redirections exactes
    if path in redirects_config:
        location = redirects_config[path]
        # Considérer comme permanent si commence par /
        permanent = location.startswith('/')
        return location, permanent

    # TODO: Ajouter support pour les patterns (regex) si nécessaire

    return None

def build_redirect_response(location: str, permanent: bool = False) -> bytes:
    """
    Construit une réponse de redirection.

    Args:
        location: URL de destination
        permanent: True pour 301, False pour 302

    Returns:
        bytes: Réponse HTTP
    """
    code = 301 if permanent else 302
    status = "Moved Permanently" if permanent else "Found"

    response = (
        f"HTTP/1.1 {code} {status}\r\n"
        f"Location: {location}\r\n"
        f"Content-Length: 0\r\n"
        f"Connection: close\r\n"
        f"\r\n"
    )
    return response.encode('utf-8')
