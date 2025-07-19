'''
This module defines the IStrategy interface that all trading strategies must implement.
'''

from abc import ABC, abstractmethod

import pandas as pd


class IStrategy(ABC):
    
    @abstractmethod
    def generate_signals(self) -> pd.DataFrame:
        """
        Should return a DataFrame with at least a 'Signal' column:
        Signal = 1 for long, -1 for short, 0 for flat
        """
        pass

    @abstractmethod
    def validate_data(self) -> None:
        """
        Validate the data before running the strategy.
        """
        pass

