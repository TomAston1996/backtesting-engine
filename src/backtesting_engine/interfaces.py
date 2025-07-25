'''
This module defines the interfaces for the backtesting engine.
'''

from dataclasses import dataclass

import pandas as pd


@dataclass
class EngineContext:
    data: pd.DataFrame
    initial_cash: float
    portfolio: dict[str, float]
    slippage: float = 0.0
    commission: float = 0.0

@dataclass
class TradeLogEntry:
    timestamp: pd.Timestamp
    ticker: str
    action: str
    shares: int
    price: float


@dataclass
class BacktestMetrics:
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    volatility: float

    def to_dict(self) -> dict[str, float]:
        return {
            "Total Return": self.total_return,
            "Sharpe Ratio": self.sharpe_ratio,
            "Max Drawdown": self.max_drawdown,
            "Volatility": self.volatility
        }

