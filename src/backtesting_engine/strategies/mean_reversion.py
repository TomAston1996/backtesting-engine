'''
Mean Reversion Strategy Implementation

Mean Reversion Strategy is a trading strategy that assumes that the price of an asset will revert to its mean or
average price over time. This strategy is based on the idea that prices fluctuate around a long-term average, and when
they deviate significantly from this average, they are likely to return to it.

Signals:
    - Buy signal (1) is generated when the current price is below the moving average by a certain threshold percentage.
    - Sell signal (-1) is generated when the current price is above the moving average by a certain threshold percentage.
'''

import numpy as np
import pandas as pd

from backtesting_engine.constants import CLOSE_COLUMN, SIGNAL_COLUMN
from backtesting_engine.exceptions import InvalidDataError
from backtesting_engine.strategies.constants import MA_COLUMN
from backtesting_engine.strategies.interfaces import IStrategy


class MeanReversionStrategy(IStrategy):
    def __init__(self, data: pd.DataFrame, window: int, threshold: float) -> None:
        """
        Initialize the Mean Reversion Strategy.

        Args:
            data (pd.DataFrame): DataFrame containing historical stock data with a 'Close' column.
            window (int): The window size for calculating the moving average. Common values are 20, 50, etc.
            threshold (float): The threshold percentage for generating buy/sell signals. Common values are 0.01 (1%), 0.02 (2%), etc.
        Raises:
            InvalidDataError: If the data length is less than the window size.
        """
        self.data = data
        self.window = window
        self.threshold = threshold
        self._validate_data()

    def _validate_data(self) -> None:
        if len(self.data) < self.window:
            raise InvalidDataError("Data length must be greater than the moving average window.")

    def generate_signals(self) -> pd.DataFrame:
        df = self.data.copy()

        df[MA_COLUMN] = df[CLOSE_COLUMN].rolling(window=self.window).mean()

        df[SIGNAL_COLUMN] = 0

        df[SIGNAL_COLUMN] = np.where(
            df[CLOSE_COLUMN] < df[MA_COLUMN] * (1 - self.threshold), 1, df[SIGNAL_COLUMN]
        )

        df[SIGNAL_COLUMN] = np.where(
            df[CLOSE_COLUMN] > df[MA_COLUMN] * (1 + self.threshold), -1, df[SIGNAL_COLUMN]
        )

        df[SIGNAL_COLUMN] = df[SIGNAL_COLUMN].shift(1)

        return df
