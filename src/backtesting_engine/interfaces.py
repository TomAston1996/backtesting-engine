"""
This module defines the interfaces for the backtesting engine.
"""

from dataclasses import dataclass
from typing import Any, Literal

import pandas as pd

from backtesting_engine.analytics.interfaces import IMetricsCreator, IPlotGenerator
from backtesting_engine.strategies.interfaces import IStrategy


@dataclass
class EngineConfig:
    slippage: float = 0.0
    commission: float = 0.0
    initial_cash: float = 100_000.0  # Default initial cash for backtesting
    generate_output: bool = True  # Whether to generate output files


@dataclass
class EngineContext:
    sim_group: str # Group name for simulation - this can be used to differentiate between a group of backtests
    sim_id: str  # Unique identifier for the simulation
    data: pd.DataFrame
    ticker: str
    strategy: IStrategy
    metrics_creator: type[IMetricsCreator]
    plot_generator: type[IPlotGenerator]


@dataclass
class TradeLogEntry:
    timestamp: pd.Timestamp
    ticker: str
    action: str
    shares: int
    price: float


@dataclass
class StrategyConfig:
    type: str
    fields: dict[str, Any]


@dataclass
class DataConfig:
    ticker: str
    start_date: str
    end_date: str
    source: Literal["yfinance", "csv"] = "yfinance"


@dataclass
class SimConfig:
    initial_cash: float
    slippage: float
    commission: float


@dataclass
class SimItem:
    sim_id: str
    strategy: StrategyConfig
    data: DataConfig
    sim_config: SimConfig


@dataclass
class QueueConfig:
    sim_group: str
    output_dir_location: str
    author: str
    sims: list[SimItem]
