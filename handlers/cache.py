"""
Système de cache LRU
"""
# Implémenter le cache LRU
from collections import OrderedDict
import time
import logging

logger = logging.getLogger("cache")


class LRUCache:
    def __init__(self, capacity=100):
        self.capacity = capacity
        self.cache = OrderedDict()
        self.hits = 0
        self.miss = 0

    def get(self, key):
        if key not in self.cache:
            self.miss += 1
            return None

        # Marquer comme récemment utilisé
        self.cache.move_to_end(key)
        self.hits += 1
        return self.cache[key]

    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)

        self.cache[key] = value

        if len(self.cache) > self.capacity:
            evicted_key, _ = self.cache.popitem(last=False)
            logger.info(f"Cache éviction : {evicted_key}")

    def clear(self):
        self.cache.clear()
        logger.warning("Cache vidé manuellement")

    def stats(self):
        """Retourne les statistiques du cache (taille, hits, miss)."""
        return {
            "size": len(self.cache),
            "hits": self.hits,
            "miss": self.miss
        }
import hashlib
import os
import time
from collections import OrderedDict
from typing import Any, Optional, Tuple

class LRUCache:
    """
    Cache LRU (Least Recently Used) thread-safe pour les fichiers statiques.
    """

    def __init__(self, capacity: int = 100):
        """
        Initialise le cache.

        Args:
            capacity: Nombre maximum d'éléments dans le cache
        """
        self.cache = OrderedDict()
        self.capacity = capacity
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[Any]:
        """
        Récupère un élément du cache.

        Args:
            key: Clé de l'élément

        Returns:
            L'élément ou None si absent
        """
        if key in self.cache:
            # Déplacer à la fin (plus récemment utilisé)
            self.cache.move_to_end(key)
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None

    def put(self, key: str, value: Any) -> None:
        """
        Ajoute ou met à jour un élément dans le cache.

        Args:
            key: Clé de l'élément
            value: Valeur à stocker
        """
        if key in self.cache:
            # Déplacer à la fin
            self.cache.move_to_end(key)
        else:
            # Nouveau élément - évincer le moins récemment utilisé si nécessaire
            if len(self.cache) >= self.capacity:
                self.cache.popitem(last=False)

        self.cache[key] = value

    def invalidate(self, key: str) -> None:
        """
        Invalide un élément du cache.

        Args:
            key: Clé à invalider
        """
        self.cache.pop(key, None)

    def clear(self) -> None:
        """Vide complètement le cache."""
        self.cache.clear()

    def size(self) -> int:
        """Retourne le nombre d'éléments dans le cache."""
        return len(self.cache)
    
    def get_stats(self):
        """Retourne les statistiques du cache."""
        return {
            'hits': self.hits,
            'misses': self.misses,
            'size': len(self.cache),
            'capacity': self.capacity
        }

def generate_etag(content: bytes) -> str:
    """
    Génère un ETag basé sur le contenu.

    Args:
        content: Contenu du fichier

    Returns:
        str: ETag (hash MD5)
    """
    return f'"{hashlib.md5(content).hexdigest()}"'

def should_use_cache(file_path: str, cached_mtime: float) -> bool:
    """
    Vérifie si le fichier n'a pas changé depuis la mise en cache.

    Args:
        file_path: Chemin du fichier
        cached_mtime: Timestamp de modification en cache

    Returns:
        bool: True si le cache est valide
    """
    try:
        current_mtime = os.path.getmtime(file_path)
        return current_mtime <= cached_mtime
    except OSError:
        return False

# Instance globale du cache
cache = LRUCache()
