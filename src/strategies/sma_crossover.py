"""
Simple Moving Average (SMA) Crossover Strategy Implementation
"""

import numpy as np
import pandas as pd

from src.strategies.interfaces import IStrategy
from src.strategies.exceptions import InvalidDataError


class SMACrossoverStrategy(IStrategy):
    def __init__(self, data: pd.DataFrame, short_window: int, long_window: int) -> None:
        self.data = data
        self.short_window = short_window
        self.long_window = long_window
        self.validate_data()

    def validate_data(self) -> None:
        """Validate the input data for the strategy."""

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
        """
        Generate trading signals based on SMA crossover strategy.

        Signals:
        - 1 for long position (short SMA crosses above long SMA) = bullish crossover
        - -1 for short position (short SMA crosses below long SMA) = bearish crossover
        - 0 for no position (no crossover) = hold position
        """
        df = self.data.copy()

        df["Short_MA"] = df["Close"].rolling(window=self.short_window).mean()
        df["Long_MA"] = df["Close"].rolling(window=self.long_window).mean()

        df["Signal"] = 0
        df["Signal"] = np.where(df["Short_MA"] > df["Long_MA"], 1, 0)
        df["Signal"] = np.where(df["Short_MA"] < df["Long_MA"], -1, df["Signal"])

        df["Signal"] = df["Signal"].shift(1)

        return df
