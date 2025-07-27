"""
Main entry point for the backtesting engine.

This script initializes the backtesting engine with a sample strategy and runs the backtest for
test purposes.
"""

from backtesting_engine.data.data_loader import DataLoader
from backtesting_engine.data.lru_cache import PersistentLRUCache
from backtesting_engine.engine import BTXEngine
from backtesting_engine.interfaces import EngineConfig, EngineContext
from backtesting_engine.metrics import BacktestMetricCreator
from backtesting_engine.strategies.sma_crossover import SMACrossoverStrategy


if __name__ == "__main__":
    TICKER = "AAPL"
    START_DATE = "2020-01-01"
    END_DATE = "2023-01-01"

    data_loader = DataLoader(cache=PersistentLRUCache())
    data = data_loader.load(ticker=TICKER, start_date=START_DATE, end_date=END_DATE, source="yfinance")

    engine = BTXEngine(
        config=EngineConfig(initial_cash=100000.0, slippage=0.01, commission=0.001),
        context=EngineContext(
            data=data,
            ticker=TICKER,
            strategy=SMACrossoverStrategy(data=data, short_window=20, long_window=50),
            metrics_creator=BacktestMetricCreator,
        ),
    )

    engine.run_backtest()
