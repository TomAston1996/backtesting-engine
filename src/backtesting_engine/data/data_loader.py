'''
Loads historical stock data from Yahoo Finance and caches it using a persistent LRU cache.
This allows for efficient retrieval of data without repeated network requests.
'''

import pandas as pd
import yfinance as yf

from backtesting_engine.data.lru_cache import CacheKey, PersistentLRUCache


lru_cache = PersistentLRUCache()


def load_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Load historical stock data from Yahoo Finance.
    """
    cache_key = CacheKey(ticker=ticker, start_date=start_date, end_date=end_date)

    if lru_cache.has(cache_key):
        print(f"Loading {ticker} from cache")
        return lru_cache.get(cache_key)

    df = yf.download(ticker, start=start_date, end=end_date)

    # remove multi-index ticker columns if they exist since we are only dealing with single ticker data
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)

    lru_cache.set(cache_key, df)
    return df
