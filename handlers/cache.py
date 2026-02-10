"""
Système de cache LRU
"""

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
            print(f"✅ CACHE HIT: {key}")
            return self.cache[key]
        self.misses += 1
        print(f"❌ CACHE MISS: {key}")
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
            print(f"🔄 CACHE UPDATE: {key}")
        else:
            # Nouveau élément
            if len(self.cache) >= self.capacity:
                # Évincer le moins récemment utilisé
                evicted = self.cache.popitem(last=False)
                print(f"🗑️  CACHE EVICTION: {evicted[0]} (capacité atteinte)")
            print(f"💾 CACHE ADD: {key} (taille: {len(self.cache) + 1}/{self.capacity})")

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
