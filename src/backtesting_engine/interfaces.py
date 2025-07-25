"""
This module defines the interfaces for the backtesting engine.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

import pandas as pd

from backtesting_engine.strategies.interfaces import IStrategy


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
            "Volatility": self.volatility,
        }


class IMetricsCreator(ABC):
    @abstractmethod
    def get_total_return(self) -> float:
        pass

    @abstractmethod
    def get_sharpe_ratio(self) -> float:
        pass

    @abstractmethod
    def get_max_drawdown(self) -> float:
        pass

    @abstractmethod
    def get_volatility(self) -> float:
        pass

    @abstractmethod
    def get_backtest_metrics(self) -> type[BacktestMetrics]:
        pass


@dataclass
class EngineConfig:
    slippage: float = 0.0
    commission: float = 0.0
    initial_cash: float = 100_000.0  # Default initial cash for backtesting


@dataclass
class EngineContext:
    data: pd.DataFrame
    portfolio: dict[str, float]
    strategy: IStrategy
    metrics_creator: type[IMetricsCreator] 


@dataclass
class TradeLogEntry:
    timestamp: pd.Timestamp
    ticker: str
    action: str
    shares: int
    price: float
