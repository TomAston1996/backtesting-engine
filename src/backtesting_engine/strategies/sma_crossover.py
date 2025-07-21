"""
Simple Moving Average (SMA) Crossover Strategy Implementation

SMA Crossover Strategy is a popular trading strategy used in financial markets.

SMA is a technical indicator that calculates the average of a selected range of prices between
a specific number of periods:

SMA = (P1 + P2 + ... + Pn) / n

The SMS Crossover Strategy calculates the short-term and long-term Simple Moving Averages (SMA) of 
the assets closing prices. A signal is generated based on the crossover of these two SMAs. If the
short-term SMA crosses above the long-term SMA (short-term SMA > long-term SMA), it indicates a potential 
bullish trend, and a buy signal is generated (1). Conversely, if the short-term SMA crosses below the 
long-term SMA (short-term SMA < long-term SMA), it indicates a potential bearish trend, and a sell signal 
is generated (-1). If there is no crossover, the signal remains at 0, indicating that no action should be
taken.
"""

import numpy as np
import pandas as pd

from backtesting_engine.strategies.interfaces import IStrategy
from backtesting_engine.strategies.exceptions import InvalidDataError


class SMACrossoverStrategy(IStrategy):
    def __init__(self, data: pd.DataFrame, short_window: int, long_window: int) -> None:
        self.data = data
        self.short_window = short_window
        self.long_window = long_window
        self.validate_data()

    def validate_data(self) -> None:
        if not isinstance(self.data, pd.DataFrame):
            raise InvalidDataError("Data must be a pandas DataFrame.")

        if self.data.empty:
            raise InvalidDataError("Data cannot be empty.")

        if "Close" not in self.data.columns:
            raise InvalidDataError(
                "Data must contain a 'Close' column for SMA calculations."
            )

        if len(self.data) < max(self.short_window, self.long_window):
            raise InvalidDataError(
                "Data length must be greater than the maximum of short and long window sizes."
            )

    def generate_signals(self) -> pd.DataFrame:
        df = self.data.copy()

        df["Short_MA"] = df["Close"].rolling(window=self.short_window).mean()
        df["Long_MA"] = df["Close"].rolling(window=self.long_window).mean()

        df["Signal"] = 0
        df["Signal"] = np.where(df["Short_MA"] > df["Long_MA"], 1, 0)
        df["Signal"] = np.where(df["Short_MA"] < df["Long_MA"], -1, df["Signal"])

        df["Signal"] = df["Signal"].shift(1)

        return df
