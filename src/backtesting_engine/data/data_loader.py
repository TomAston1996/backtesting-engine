"""
Loads historical stock data from Yahoo Finance and caches it using a persistent LRU cache.
This allows for efficient retrieval of data without repeated network requests.
"""

from typing import Literal, Optional

import pandas as pd
import yfinance as yf

from backtesting_engine.data.interfaces import ILocalCache
from backtesting_engine.data.lru_cache import CacheKey, PersistentLRUCache


class DataLoader:
    """
    DataLoader is responsible for loading historical stock data from various sources.

    It supports loading from Yahoo Finance or a CSV file, and utilizes a persistent LRU cache
    to avoid redundant data fetching.
    """

    def __init__(self, cache: Optional[ILocalCache] = None) -> None:
        self.cache = cache or PersistentLRUCache()

    def load(
        self,
        ticker: str,
        start_date: str,
        end_date: str,
        source: Literal["yfinance", "csv"] = "yfinance",
        csv_path: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Load historical stock data from either Yahoo Finance or a CSV file.
        """

        if source == "csv":
            if not csv_path:
                raise ValueError("csv_path must be provided when source='csv'")
            return self._load_from_csv(csv_path)

        if source == "yfinance":
            return self._load_from_yfinance(ticker, start_date, end_date)

    def _load_from_yfinance(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        cache_key = CacheKey(ticker, start_date, end_date)

        if self.cache.has(cache_key):
            print(f"[CACHE HIT] {ticker} {start_date} to {end_date}")
            return self.cache.get(cache_key)

        print(f"[CACHE MISS] Downloading {ticker} from Yahoo Finance")
        df = yf.download(ticker, start=start_date, end=end_date)

        # Ensure the DataFrame has a single level of columns as we only deal with single ticker data
        if df is not None and isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(1)

        if df is None:
            raise ValueError(f"No data found for {ticker} from {start_date} to {end_date}")

        self.cache.set(cache_key, df)
        return df

    def _load_from_csv(self, path: str) -> pd.DataFrame:
        print(f"[CSV LOAD] Loading data from {path}")
        df = pd.read_csv(path, index_col=0, parse_dates=True)

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(1)

        return df
