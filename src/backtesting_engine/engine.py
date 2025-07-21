"""
This module implements the backtesting engine for executing trading strategies.
"""

from src.strategies.interfaces import IStrategy
from src.backtesting_engine.interfaces import EngineContext


class BTXEngine:
    def __init__(self, strategy: IStrategy, context: EngineContext) -> None:
        self.data = context.data
        self.strategy = strategy

    def run_backtest(self) -> None:
        # Placeholder for backtesting logic
        print("Running backtest on the provided data...")
        print(self.strategy.generate_signals())
