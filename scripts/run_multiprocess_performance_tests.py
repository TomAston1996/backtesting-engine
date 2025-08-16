"""
Run performance tests for the backtesting engine using multiprocessing.

This script runs multiple backtest simulations both sequentially and in parallel, and compares the performance of both approaches.
It generates a plot to visualize the results.
"""

import os
import time

from functools import wraps
from typing import Callable, ParamSpec, TypeVar

import matplotlib.pyplot as plt
import numpy as np

from backtesting_engine.analytics.metrics import BacktestMetricCreator
from backtesting_engine.analytics.plotter import PlotGenerator
from backtesting_engine.data.data_loader import DataLoader
from backtesting_engine.data.lru_cache import PersistentLRUCache
from backtesting_engine.engine import BTXEngine
from backtesting_engine.interfaces import EngineConfig, EngineContext
from backtesting_engine.managers import QueueManager
from backtesting_engine.strategies.sma_crossover import SMACrossoverStrategy


RESULTS_DIR = "data/performance_test_results/"

P = ParamSpec("P")
R = TypeVar("R")


def timed(name: str) -> Callable[[Callable[P, R]], Callable[P, tuple[R, float]]]:
    """Decorator that returns both the function result and elapsed time."""

    def decorator(func: Callable[P, R]) -> Callable[P, tuple[R, float]]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> tuple[R, float]:
            start = time.perf_counter()
            result = func(*args, **kwargs)
            end = time.perf_counter()
            elapsed = end - start
            print(f"[{name}] took {elapsed:.6f} seconds")
            return result, elapsed

        return wrapper

    return decorator


def run_single_sim(sim_id: int) -> None:
    """
    Run a single backtest simulation with a sample strategy.

    This just runs sma_crossover strategy with AAPL data from 2020-01-01 to 2023-01-01.
    This is to match what is run on multiple simulation runs in `run_multiple_sims_with_multiprocessing`.
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
            sim_id=str(sim_id),
            data=data,
            ticker=TICKER,
            strategy=SMACrossoverStrategy(data=data, short_window=50, long_window=100),
            metrics_creator=BacktestMetricCreator,
            plot_generator=PlotGenerator,
        ),
    )

    engine.run_backtest()


@timed("SEQUENTIAL_RUN")
def run_multiple_sims_without_multiprocessing(num_loops: int) -> None:
    """
    Run multiple simulations sequentially without multiprocessing.

    This runs the same simulation multiple times, which will be compared against the
    multiprocessing version in `run_multiple_sims_with_multiprocessing`.
    """
    for sim_id in range(num_loops):
        run_single_sim(sim_id)


@timed("MULTIPROCESSING_RUN")
def run_multiple_sims_with_multiprocessing(test_file_name: str) -> None:
    """
    Run multiple simulations using the queue manager which handles multiprocessing.

    test_queue_config.json just contains a repetition of the same simulation for testing purposes. It
    is currently just sma_crossover strategy with AAPL data from 2020-01-01 to 2023-01-01. This is to
    match what is run on single simulation runs in `run_single_sim`.
    """
    queue_manager = QueueManager(queue_file_path=test_file_name)
    queue_manager.run_all()


def plot_performance_results(results: list[dict[str, float]]) -> None:
    """
    Plot the performance results of sequential vs multiprocessing runs.
    """
    os.makedirs(RESULTS_DIR, exist_ok=True)

    sim_sizes = [str(r["num_sims"]) for r in results]
    sequential_times = [r["sequential_time"] for r in results]
    multiprocessing_times = [r["multiprocessing_time"] for r in results]

    # Setup bar positions
    x = np.arange(len(sim_sizes))  # label locations
    width = 0.35  # width of bars

    _, ax = plt.subplots(figsize=(10, 6))

    # Plot bars
    ax.bar(x - width / 2, sequential_times, width, label="Sequential", color="lightgrey")
    ax.bar(x + width / 2, multiprocessing_times, width, label="Multiprocessing", color="teal")

    # Labels, title, legend
    ax.set_xlabel("Number of Simulations")
    ax.set_ylabel("Elapsed Time (seconds)")
    ax.set_title("Sequential vs Multiprocessing Performance")
    ax.set_xticks(x)
    ax.set_xticklabels(sim_sizes)
    ax.legend()

    output_path = os.path.join(RESULTS_DIR, "performance_comparison.png")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Saved performance plot to {output_path}")


if __name__ == "__main__":
    simulation_sizes = [5, 50, 100, 300]
    simulation_test_files = [
        f"data/performance_test_files/test_queue_file_{size}_sims.json" for size in simulation_sizes
    ]

    results = []

    for size, file in zip(simulation_sizes, simulation_test_files):
        _, seq_time = run_multiple_sims_without_multiprocessing(size)

        _, mp_time = run_multiple_sims_with_multiprocessing(file)

        results.append(
            {
                "num_sims": size,
                "sequential_time": seq_time,
                "multiprocessing_time": mp_time,
            }
        )

    plot_performance_results(results)
