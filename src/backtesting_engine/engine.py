import pandas as pd

from src.strategies.interfaces import IStrategy

class BTXEngine:
    
    def __init__(self, data: pd.DataFrame, strategy: IStrategy) -> None:
        self.data = data
        self.strategy = strategy

    def run_backtest(self) -> None:
        # Placeholder for backtesting logic
        print("Running backtest on the provided data...")
        print(self.strategy.generate_signals())