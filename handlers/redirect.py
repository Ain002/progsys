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
