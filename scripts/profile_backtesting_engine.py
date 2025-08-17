"""
Script for profiling the backtesting engine using cProfile and viewing results with snakeviz.
"""

import cProfile
import os

from backtesting_engine.analytics.metrics import BacktestMetricCreator
from backtesting_engine.analytics.plotter import PlotGenerator
from backtesting_engine.data.data_loader import DataLoader
from backtesting_engine.data.lru_cache import PersistentLRUCache
from backtesting_engine.engine import BTXEngine
from backtesting_engine.interfaces import EngineConfig, EngineContext
from backtesting_engine.strategies.sma_crossover import SMACrossoverStrategy


def run_single_sim() -> None:
    """
    Run a single backtest simulation with a sample strategy.

    This just runs sma_crossover strategy with AAPL data from 2020-01-01 to 2023-01-01.
    """
    TICKER = "AAPL"
    START_DATE = "2020-01-01"
    END_DATE = "2023-01-01"

    data_loader = DataLoader(cache=PersistentLRUCache())
    data = data_loader.load(ticker=TICKER, start_date=START_DATE, end_date=END_DATE, source="yfinance")

    engine = BTXEngine(
        config=EngineConfig(initial_cash=100_000.0, slippage=0.01, commission=0.001),
        context=EngineContext(
            sim_group="local_test",
            sim_id="001",
            data=data,
            ticker=TICKER,
            strategy=SMACrossoverStrategy(data=data, short_window=50, long_window=100),
            metrics_creator=BacktestMetricCreator,
            plot_generator=PlotGenerator,
        ),
    )

    engine.run_backtest()


def run_cprofiled_sim() -> None:
    """
    Run a single backtest simulation with profiling enabled,
    and open results in snakeviz.
    """
    profile_file = "profile_results.prof"

    profiler = cProfile.Profile()
    profiler.enable()

    run_single_sim()

    profiler.disable()
    profiler.dump_stats(profile_file)

    # Launch snakeviz on the profile file
    os.system(f"snakeviz {profile_file}")

if __name__ == "__main__":
    run_cprofiled_sim()
