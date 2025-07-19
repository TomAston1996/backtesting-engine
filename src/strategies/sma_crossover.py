import numpy as np
import pandas as pd

from src.strategies.interfaces import IStrategy


class SMACrossoverStrategy(IStrategy):
    def __init__(self, data: pd.DataFrame, short_window: int, long_window: int) -> None:
        self.data = data
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self) -> pd.DataFrame:
        signals = pd.DataFrame(index=self.data.index)
        
        signals['short_mavg'] = self.data['Close'].rolling(window=self.short_window, min_periods=1).mean()
        signals['long_mavg'] = self.data['Close'].rolling(window=self.long_window, min_periods=1).mean()
        
        signals['signal'] = 0
        signals['signal'][self.short_window:] = np.where(
            signals['short_mavg'][self.short_window:] > signals['long_mavg'][self.short_window:], 1, 0
        )
        
        signals['positions'] = signals['signal'].diff()
        
        return signals