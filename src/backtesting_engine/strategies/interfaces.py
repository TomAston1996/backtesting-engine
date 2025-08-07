"""
This module defines the IStrategy interface that all trading strategies must implement.
"""

from abc import ABC, abstractmethod

import pandas as pd


class IStrategy(ABC):
    @abstractmethod
    def generate_signals(self) -> pd.DataFrame:
        """
        Generate trading signals based on strategy.

        Signals:
        - 1 for long position
        - -1 for short position
        - 0 for hold position

        Returns:
            pd.DataFrame: DataFrame containing the generated signals and any additional data.
        """
        pass
