import pandas as pd
import yfinance as yf


def load_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Load historical stock data from Yahoo Finance.
    """
    df = yf.download(ticker, start=start_date, end=end_date)

    # remove multi-index ticker columns if they exist since we are only dealing with single ticker data
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1) 
    
    return df