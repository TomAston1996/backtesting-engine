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

Signals:
    - Buy signal (1) is generated when the short-term SMA crosses above the long-term SMA
    - Sell signal (-1) is generated when the short-term SMA crosses below the long-term SMA
    - Hold signal (0) is generated when there is no crossover
"""

import numpy as np
import pandas as pd

from backtesting_engine.constants import CLOSE_COLUMN, SIGNAL_COLUMN
from backtesting_engine.exceptions import InvalidDataError
from backtesting_engine.strategies.constants import LONG_MA_COLUMN, SHORT_MA_COLUMN
from backtesting_engine.strategies.interfaces import IStrategy


class SMACrossoverStrategy(IStrategy):
    def __init__(self, data: pd.DataFrame, short_window: int, long_window: int) -> None:
        """
        Initialize the SMA Crossover Strategy.

        Args:
            data (pd.DataFrame): DataFrame containing historical stock data with a 'Close' column.
            short_window (int): The window size for the short-term moving average. Common values are 10, 20, etc.
            long_window (int): The window size for the long-term moving average. Common values are 50, 100, etc.
        Raises:
            InvalidDataError: If the data length is less than the maximum of short and long window sizes.
        """
        self.data = data
        self.short_window = short_window
        self.long_window = long_window
        self._validate_data()

    def _validate_data(self) -> None:
        if len(self.data) < max(self.short_window, self.long_window):
            raise InvalidDataError(
                "Data length must be greater than the maximum of short and long window sizes."
            )

    def generate_signals(self) -> pd.DataFrame:
        df = self.data.copy()

        df[SHORT_MA_COLUMN] = df[CLOSE_COLUMN].rolling(window=self.short_window).mean()
        df[LONG_MA_COLUMN] = df[CLOSE_COLUMN].rolling(window=self.long_window).mean()

        df[SIGNAL_COLUMN] = 0
        df[SIGNAL_COLUMN] = np.where(df[SHORT_MA_COLUMN] > df[LONG_MA_COLUMN], 1, 0)
        df[SIGNAL_COLUMN] = np.where(df[SHORT_MA_COLUMN] < df[LONG_MA_COLUMN], -1, df[SIGNAL_COLUMN])

        df[SIGNAL_COLUMN] = df[SIGNAL_COLUMN].shift(1)

        return df
