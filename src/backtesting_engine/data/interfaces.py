'''
This module defines the interfaces used within the backtesting engine's data layer.
'''

from abc import ABC, abstractmethod
from typing import Any

import pandas as pd


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


class IDataLoader (ABC):
    @abstractmethod
    def load(self, *args: Any, **kwargs: Any) -> pd.DataFrame:...

    @abstractmethod
    def validate_data(self, df: pd.DataFrame) -> None:...
