"""
This module implements a simple LRU (Least Recently Used) cache that persists to disk. It allows for
efficient caching of data, such as historical stock prices, to avoid repeated network requests
and improve performance in our backtesting engine especially when running multiple simulations
sequentially or in parallel.

Pickle is used as we are storing complex objects (like DataFrames) that need to be serialized.
"""

import os
import pickle

from collections import OrderedDict
from typing import Any, NamedTuple

from filelock import FileLock

from backtesting_engine.data.interfaces import ILocalCache


class CacheKey(NamedTuple):
    ticker: str
    start_date: str
    end_date: str

    def __str__(self) -> str:
        return f"{self.ticker}_{self.start_date}_{self.end_date}"


class PersistentLRUCache(ILocalCache):
    """A simple LRU cache implementation that persists to disk using pickle."""

    def __init__(self, cache_dir: str = ".cache", cache_file: str = "lru_cache.pkl", max_size: int = 10) -> None:
        self.cache_dir = cache_dir
        self.cache_path = os.path.join(cache_dir, cache_file)
        self.lock_path = self.cache_path + ".lock"
        self.max_size = max_size

        os.makedirs(self.cache_dir, exist_ok=True)
        self._cache = OrderedDict()
        self._lock = FileLock(self.lock_path)

        self._load_cache()

    def _load_cache(self) -> None:
        """Load the cache from disk."""
        with self._lock:
            if os.path.exists(self.cache_path):
                try:
                    with open(self.cache_path, "rb") as f:
                        self._cache = pickle.load(f)
                except (EOFError, pickle.UnpicklingError):
                    print(f"Cache file {self.cache_path} is corrupted or empty. Starting with an empty cache.")
                    self._cache = OrderedDict()

    def _save_cache(self) -> None:
        """Save the cache to disk atomically."""
        with self._lock:
            temp_path = self.cache_path + ".tmp"
            with open(temp_path, "wb") as f:
                pickle.dump(self._cache, f)
            os.replace(temp_path, self.cache_path)

    def get(self, key: CacheKey) -> Any:
        """Get an item from the cache."""
        if key in self._cache:
            self._cache.move_to_end(key)
            self._save_cache()
            return self._cache[key]
        return None

    def set(self, key: CacheKey, value: Any) -> None:
        """Set an item in the cache."""
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = value

        # Evict least recently used if over max_size
        if len(self._cache) > self.max_size:
            self._cache.popitem(last=False)

        self._save_cache()

    def has(self, key: CacheKey) -> bool:
        """Check if an item exists in the cache."""
        return key in self._cache

    def clear(self) -> None:
        """Clear the cache."""
        self._cache = OrderedDict()
        self._save_cache()
