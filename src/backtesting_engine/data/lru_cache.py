"""
This module implements a simple LRU (Least Recently Used) cache that persists to disk. It allows for
efficient caching of data, such as historical stock prices, to avoid repeated network requests
and improve performance in our backtesting engine especially when running multiple simulations
sequentially or in parallel.

Pickle is used as we are storing complex objects (like DataFrames) that need to be serialized.
"""

import os
import pickle

from collections import OrderedDict, namedtuple
from typing import Any


CacheKey = namedtuple("CacheKey", ["ticker", "start_date", "end_date"])


class PersistentLRUCache:
    """A simple LRU cache implementation that persists to disk using pickle.

    #TODO: this needs to be made thread-safe if used in a multi-threaded environment with FileLock
    """

    def __init__(self, cache_dir: str = ".cache", cache_file: str = "lru_cache.pkl", max_size: int = 10) -> None:
        self.cache_dir = cache_dir
        self.cache_path = os.path.join(cache_dir, cache_file)
        self.max_size = max_size

        os.makedirs(self.cache_dir, exist_ok=True)
        self._cache = self._load_cache()

    def _load_cache(self) -> OrderedDict:
        if os.path.exists(self.cache_path):
            with open(self.cache_path, "rb") as f:
                return pickle.load(f)
        return OrderedDict()

    def _save_cache(self) -> None:
        with open(self.cache_path, "wb") as f:
            pickle.dump(self._cache, f)

    def get(self, key: CacheKey) -> Any:
        if key in self._cache:
            self._cache.move_to_end(key)
            return self._cache[key]
        return None

    def set(self, key: CacheKey, value: Any) -> None:
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = value

        # Evict least recently used if over max_size
        if len(self._cache) > self.max_size:
            self._cache.popitem(last=False)

        self._save_cache()

    def has(self, key: CacheKey) -> bool:
        return key in self._cache

    def clear(self) -> None:
        self._cache = OrderedDict()
        self._save_cache()
