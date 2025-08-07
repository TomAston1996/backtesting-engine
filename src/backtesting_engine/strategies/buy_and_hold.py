'''
Buy and Hold Strategy Implementation

The Buy and Hold Strategy is a passive investment strategy where an investor buys stocks and holds them for a long
period, regardless of market fluctuations. The strategy is based on the belief that, over time, the stock market will
increase in value, and holding onto investments will yield positive returns.

Signals:
    - Buy signal (1) is generated at the start of the investment period
'''

import pandas as pd

from backtesting_engine.constants import SIGNAL_COLUMN
from backtesting_engine.exceptions import InvalidDataError
from backtesting_engine.strategies.interfaces import IStrategy


class BuyAndHoldStrategy(IStrategy):
    def __init__(self, data: pd.DataFrame) -> None:
        """
        Initialize the Buy and Hold Strategy.

        Args:
            data (pd.DataFrame): DataFrame containing historical stock data with a 'Close' column.
        Raises:
            InvalidDataError: If the data length is less than 2.
        """
        self.data = data
        self._validate_data()

    def _validate_data(self) -> None:
        if len(self.data) < 2:
            raise InvalidDataError("Not enough data to apply Buy and Hold strategy.")

    def generate_signals(self) -> pd.DataFrame:
        df = self.data.copy()
        df[SIGNAL_COLUMN] = 1  # Always long
        df[SIGNAL_COLUMN] = df[SIGNAL_COLUMN].shift(1)  # Enter on the next bar
        return df
