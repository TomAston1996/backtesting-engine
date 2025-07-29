import os
import shutil
import tempfile

from typing import Any, Generator

import pytest

from backtesting_engine.data.lru_cache import CacheKey, PersistentLRUCache


@pytest.fixture
def temp_cache_dir() -> Generator[str, None, None]:
    """Creates a temporary cache directory and cleans it up after tests."""
    dirpath = tempfile.mkdtemp()
    yield dirpath
    shutil.rmtree(dirpath)


def test_set_and_get(temp_cache_dir: str) -> None:
    # Arrange
    cache = PersistentLRUCache(cache_dir=temp_cache_dir, max_size=2)
    key = CacheKey("AAPL", "2023-01-01", "2023-01-31")
    value = {"price": [100, 101, 102]}

    # Act
    cache.set(key, value)

    # Assert
    assert cache.get(key) == value
    assert cache.has(key)


def test_lru_eviction(temp_cache_dir: str) -> None:
    # Arrange
    cache = PersistentLRUCache(cache_dir=temp_cache_dir, max_size=2)

    k1 = CacheKey("AAPL", "2023-01-01", "2023-01-31")
    k2 = CacheKey("MSFT", "2023-01-01", "2023-01-31")
    k3 = CacheKey("GOOG", "2023-01-01", "2023-01-31")

    # Act
    cache.set(k1, 1)
    cache.set(k2, 2)
    cache.set(k3, 3)

    # Assert
    assert not cache.has(k1)  # Should be evicted
    assert cache.has(k2)
    assert cache.has(k3)


def test_clear(temp_cache_dir: str) -> None:
    # Arrange
    cache = PersistentLRUCache(cache_dir=temp_cache_dir, max_size=2)
    key = CacheKey("AAPL", "2023-01-01", "2023-01-31")
    cache.set(key, 123)

    # Act
    cache.clear()

    # Assert
    assert not cache.has(key)
    assert cache.get(key) is None


def test_persistence(temp_cache_dir: str) -> None:
    # Arrange
    key = CacheKey("AAPL", "2023-01-01", "2023-01-31")
    value = {"price": [100, 200, 300]}
    cache1 = PersistentLRUCache(cache_dir=temp_cache_dir, max_size=5)

    # Act
    cache1.set(key, value)
    cache2 = PersistentLRUCache(cache_dir=temp_cache_dir, max_size=5)

    # Assert
    assert cache2.get(key) == value


def test_overwrite_existing_key(temp_cache_dir: str) -> None:
    # Arrange
    cache = PersistentLRUCache(cache_dir=temp_cache_dir, max_size=2)
    key = CacheKey("AAPL", "2023-01-01", "2023-01-31")

    # Act
    cache.set(key, 123)
    cache.set(key, 456)  # overwrite

    # Assert
    assert cache.get(key) == 456


def test_corrupted_cache_file_handled_gracefully(temp_cache_dir: str, capsys: Any) -> None:
    # Arrange
    bad_file_path = os.path.join(temp_cache_dir, "lru_cache.pkl")
    with open(bad_file_path, "wb") as f:
        f.write(b"not a valid pickle")

    # Act and Assert
    PersistentLRUCache(cache_dir=temp_cache_dir, max_size=3)
    captured = capsys.readouterr()
    assert "corrupted or empty" in captured.out
