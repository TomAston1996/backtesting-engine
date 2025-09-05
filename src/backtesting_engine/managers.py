"""
This module manages the queue for backtesting simulations, loading configurations from a JSON file,
and running simulations based on the specified strategies and data.
"""

import json
import multiprocessing as mp

from multiprocessing import Queue
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from backtesting_engine.analytics.metrics import BacktestMetricCreator
from backtesting_engine.analytics.plotter import PlotGenerator
from backtesting_engine.constants import (
    AUTHOR,
    DATA,
    OUTPUT_DIR_LOCATION,
    SIM_CONFIG,
    SIM_GROUP,
    SIM_ID,
    SIMS,
    STRATEGY,
)
from backtesting_engine.data.data_loader import DataLoader
from backtesting_engine.data.lru_cache import PersistentLRUCache
from backtesting_engine.engine import BTXEngine
from backtesting_engine.interfaces import (
    DataConfig,
    EngineConfig,
    EngineContext,
    QueueConfig,
    SimConfig,
    SimItem,
    StrategyConfig,
)
from backtesting_engine.strategies.buy_and_hold import BuyAndHoldStrategy
from backtesting_engine.strategies.mean_reversion import MeanReversionStrategy
from backtesting_engine.strategies.momentum import MomentumStrategy
from backtesting_engine.strategies.sma_crossover import SMACrossoverStrategy


if TYPE_CHECKING:
    JobQueueType = Queue[SimItem]  # For static type checking
else:
    JobQueueType = Queue


STRATEGIES = {
    "sma_crossover": SMACrossoverStrategy,
    "mean_reversion": MeanReversionStrategy,
    "momentum": MomentumStrategy,
    "buy_and_hold": BuyAndHoldStrategy,
}


class QueueManager:
    """Manages a queue loaded from a JSON file"""

    def __init__(self, queue_file_path: str, max_workers: Optional[int] = None) -> None:
        self.max_workers = max_workers if max_workers is not None else mp.cpu_count()
        self.queue_config = self._load_queue_config(queue_file_path=queue_file_path)
        self._create_output_directory()

    def _load_queue_config(self, queue_file_path: str) -> QueueConfig:
        """
        Loads the queue configuration from a JSON file and creates the output directory if it does not exist.
        """
        path = Path(queue_file_path)
        if not path.exists():
            raise FileNotFoundError(f"Queue file {queue_file_path} does not exist.")

        with path.open("r") as file:
            raw_config = json.load(file)

        sims = []
        for sim in raw_config[SIMS]:
            sims.append(
                SimItem(
                    sim_id=sim[SIM_ID],
                    strategy=StrategyConfig(**sim[STRATEGY]),
                    data=DataConfig(**sim[DATA]),
                    sim_config=SimConfig(**sim[SIM_CONFIG]),
                )
            )

        return QueueConfig(
            sim_group=raw_config[SIM_GROUP],
            output_dir_location=raw_config[OUTPUT_DIR_LOCATION],
            author=raw_config[AUTHOR],
            sims=sims,
        )

    def _create_output_directory(self) -> None:
        output_dir = Path(self.queue_config.output_dir_location)
        output_dir.mkdir(parents=True, exist_ok=True)

    def _worker(self, job_queue: "JobQueueType") -> None:
        while True:
            try:
                sim_item = job_queue.get_nowait()
            except Exception:
                break  # Queue is empty

            data_loader = DataLoader(cache=PersistentLRUCache())
            data = data_loader.load(
                ticker=sim_item.data.ticker,
                start_date=sim_item.data.start_date,
                end_date=sim_item.data.end_date,
                source=sim_item.data.source,
            )

            strategy_cls = STRATEGIES.get(sim_item.strategy.type.lower())
            if not strategy_cls:
                raise ValueError(f"Unknown strategy type: {sim_item.strategy.type}")

            strategy = strategy_cls(data=data, **sim_item.strategy.fields)

            engine = BTXEngine(
                config=EngineConfig(
                    initial_cash=sim_item.sim_config.initial_cash,
                    slippage=sim_item.sim_config.slippage,
                    commission=sim_item.sim_config.commission,
                    generate_output=False,
                ),
                context=EngineContext(
                    sim_group=self.queue_config.sim_group,
                    sim_id=sim_item.sim_id,
                    data=data,
                    ticker=sim_item.data.ticker,
                    strategy=strategy,
                    metrics_creator=BacktestMetricCreator,
                    plot_generator=PlotGenerator,
                ),
            )

            print(f"[{self.queue_config.sim_group}:{sim_item.sim_id}] Starting...")
            engine.run_backtest()
            print(f"[{self.queue_config.sim_group}:{sim_item.sim_id}] Completed.")

    def run_all(self) -> None:
        manager = mp.Manager()
        job_queue = manager.Queue()

        for sim in self.queue_config.sims:
            job_queue.put(sim)

        processes: list[mp.Process] = []
        for _ in range(self.max_workers):
            p = mp.Process(target=self._worker, args=(job_queue,))
            p.start()
            processes.append(p)

        # Wait for all workers to finish
        for p in processes:
            p.join()
