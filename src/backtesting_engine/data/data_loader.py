import pandas as pd
import yfinance as yf


def load_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Load historical stock data from Yahoo Finance.
    """
    df = yf.download(ticker, start=start_date, end=end_date)
    return df