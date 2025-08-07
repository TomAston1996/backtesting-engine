'''
This module defines the interfaces used within the backtesting engine's data layer.
'''

from abc import ABC, abstractmethod
from typing import Any


class ILocalCache(ABC):
    @abstractmethod
    def get(self, key: Any) -> Any:
        """Retrieve an item from the cache."""
        pass

    @abstractmethod
    def set(self, key: Any, value: Any) -> None:
        """Store an item in the cache."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear the entire cache."""
        pass

    @abstractmethod
    def has(self, key: Any) -> bool:
        """Check if an item exists in the cache."""
        pass
