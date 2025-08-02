"""
This module defines the interfaces for the analytics package.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class BacktestMetrics:
    ticker: str
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    volatility: float

    def to_dict(self) -> dict[str, str | float]:
        return {
            "Ticker": self.ticker,
            "Total Return": self.total_return,
            "Sharpe Ratio": self.sharpe_ratio,
            "Max Drawdown": self.max_drawdown,
            "Volatility": self.volatility,
        }

    def pretty_print(self) -> None:
        print(f"Ticker: {self.ticker}")
        print(f"Total Return: {self.total_return:.2%}")
        print(f"Sharpe Ratio: {self.sharpe_ratio:.2f}")
        print(f"Max Drawdown: {self.max_drawdown:.2%}")
        print(f"Volatility: {self.volatility:.2%}")


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
    def get_backtest_metrics(self) -> BacktestMetrics:
        pass


class IPlotGenerator(ABC):
    @abstractmethod
    def generate(self) -> None:
        pass
