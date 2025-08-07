"""
Momentum Strategy Implementation

Momentum Strategy is a trading strategy that aims to capitalize on the continuation of existing trends in the market.
The strategy is based on the idea that assets that have performed well in the past will continue to perform well in
the future, and vice versa for underperforming assets.

Signals:
    - Buy signal (1) is generated when the momentum of the asset exceeds a certain threshold
    - Sell signal (-1) is generated when the momentum of the asset falls below a certain negative threshold
    - Hold signal (0) is generated when the momentum is within the threshold range
"""

import numpy as np
import pandas as pd

from backtesting_engine.constants import CLOSE_COLUMN, SIGNAL_COLUMN
from backtesting_engine.exceptions import InvalidDataError
from backtesting_engine.strategies.constants import MOMENTUM_COLUMN
from backtesting_engine.strategies.interfaces import IStrategy


class MomentumStrategy(IStrategy):
    def __init__(self, data: pd.DataFrame, window: int, threshold: float) -> None:
        """
        Initialize the Momentum Strategy.

        Args:
            data (pd.DataFrame): DataFrame containing historical stock data with a 'Close' column.
            window (int): The window size for calculating momentum. Common values are 10, 20, etc.
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
            raise InvalidDataError("Data length must be greater than the momentum window.")

    def generate_signals(self) -> pd.DataFrame:
        df = self.data.copy()

        df[MOMENTUM_COLUMN] = df[CLOSE_COLUMN].pct_change(periods=self.window)

        df[SIGNAL_COLUMN] = 0
        df[SIGNAL_COLUMN] = np.where(df[MOMENTUM_COLUMN] > self.threshold, 1, df[SIGNAL_COLUMN])
        df[SIGNAL_COLUMN] = np.where(df[MOMENTUM_COLUMN] < -self.threshold, -1, df[SIGNAL_COLUMN])

        df[SIGNAL_COLUMN] = df[SIGNAL_COLUMN].shift(1)

        return df
