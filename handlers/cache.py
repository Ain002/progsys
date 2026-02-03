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
