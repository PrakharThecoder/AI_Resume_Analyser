import json
import os
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)
CACHE_FILE = "cache_data.json"

class PersistentCacheManager:
    def __init__(self):
        self.cache_hits = 0
        self.cache_misses = 0
        self.parsed_resumes_cache: Dict[str, dict] = {}
        self.load()

    def load(self):
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r") as f:
                    data = json.load(f)
                    self.cache_hits = data.get("cache_hits", 0)
                    self.cache_misses = data.get("cache_misses", 0)
                    self.parsed_resumes_cache = data.get("parsed_resumes_cache", {})
            except Exception as e:
                logger.warning(f"Failed to load cache data: {e}")

    def save(self):
        try:
            with open(CACHE_FILE, "w") as f:
                json.dump({
                    "cache_hits": self.cache_hits,
                    "cache_misses": self.cache_misses,
                    "parsed_resumes_cache": self.parsed_resumes_cache
                }, f)
        except Exception as e:
            logger.error(f"Failed to save cache data: {e}")

    def get_entry(self, file_hash: str) -> Optional[dict]:
        logger.info(f"CACHE CHECK hash={file_hash}")
        if file_hash in self.parsed_resumes_cache:
            self.cache_hits += 1
            self.save()
            logger.info(f"CACHE HIT hash={file_hash}")
            return self.parsed_resumes_cache[file_hash]
        
        self.cache_misses += 1
        self.save()
        logger.info(f"CACHE MISS hash={file_hash}")
        return None

    def store_entry(self, file_hash: str, parsed_data: dict):
        self.parsed_resumes_cache[file_hash] = parsed_data
        self.save()
        logger.info(f"CACHE STORE hash={file_hash}")

    def get_cached_resumes_count(self) -> int:
        return len(self.parsed_resumes_cache)

    def get_cache_keys(self) -> list:
        return list(self.parsed_resumes_cache.keys())

# Singleton instance
cache_manager = PersistentCacheManager()
