"""
This module implements the backtesting engine for executing trading strategies.
"""

from typing import Callable, cast

import pandas as pd

from backtesting_engine.analytics.interfaces import IMetricsCreator, IPlotGenerator
from backtesting_engine.constants import (
    BUY,
    CASH_COLUMN,
    CLOSE_COLUMN,
    HOLDINGS_COLUMN,
    POSITION_COLUMN,
    SELL,
    SIGNAL_COLUMN,
    TOTAL_VALUE_COLUMN,
)
from backtesting_engine.interfaces import EngineConfig, EngineContext, TradeLogEntry


class BTXEngine:
    """
    BTXEngine is the core backtesting engine that executes trading strategies. It processes
    the strategy signals and updates the portfolio accordingly.
    """

    def __init__(self, config: EngineConfig, context: EngineContext) -> None:
        # inject dependencies
        self.context = context
        self.strategy = context.strategy
        self.data = context.data.copy()
        self.ticker = context.ticker

        # metrics creator should be called after the backtest is run
        # to ensure it has the complete backtest results DataFrame
        self.metrics_creator: Callable[[pd.DataFrame, str], IMetricsCreator] = context.metrics_creator
        self.plot_generator: Callable[[pd.DataFrame, str, EngineContext], IPlotGenerator] = context.plot_generator

        self.initial_cash = config.initial_cash
        self.slippage = config.slippage
        self.commission = config.commission
        self.config = config

        self.trade_log: list[TradeLogEntry] = []

    def run_backtest(self) -> pd.DataFrame:
        """
        Run main backtest loop.
        """
        df = self.strategy.generate_signals()
        df = self._backtest_single_ticker(df, self.ticker)
        self.data = df

        # Calculate performance metrics after the backtest is complete
        metrics_creator = self.metrics_creator(df, self.ticker)
        metrics_creator.get_backtest_metrics()
        # performance_metrics.pretty_print()

        # Generate plots for the backtest results
        if self.config.generate_output:
            plot_generator = self.plot_generator(df, self.strategy.__class__.__name__, self.context)
            plot_generator.generate()

        return df

    def _backtest_single_ticker(self, df: pd.DataFrame, ticker: str) -> pd.DataFrame:
        """
        Backtest a single ticker using the strategy signals.

        This method updates the DataFrame with trading signals and portfolio values.
        """
        df.at[df.index[0], POSITION_COLUMN] = 0
        df.at[df.index[0], CASH_COLUMN] = float(self.initial_cash)
        df.at[df.index[0], HOLDINGS_COLUMN] = 0.0
        df.at[df.index[0], TOTAL_VALUE_COLUMN] = float(self.initial_cash)  # all cash on day 0

        position = 0
        cash = self.initial_cash

        for i in range(1, len(df)):
            price = df.at[df.index[i], CLOSE_COLUMN]
            if pd.isna(price):
                continue

            signal = df.at[df.index[i], SIGNAL_COLUMN]
            if pd.isna(signal):
                signal = 0.0
                df.at[df.index[i], SIGNAL_COLUMN] = 0.0

            if self._should_buy(signal, position):
                position, cash = self._execute_buy(cash, position, price, ticker, cast(pd.Timestamp, df.index[i]))

            elif self._should_sell(signal, position):
                position, cash = self._execute_sell(cash, position, price, ticker, cast(pd.Timestamp, df.index[i]))

            self._update_portfolio(df, i, position, cash, price)

        return df

    def _should_buy(self, signal: float, position: int) -> bool:
        """
        Determines if a buy action should be executed based on the signal and current position.

        A buy action is executed if the signal is 1 (indicating a buy signal) and the current position is
        0 (indicating no shares held).
        """
        return signal == 1 and position == 0

    def _should_sell(self, signal: float, position: int) -> bool:
        """
        Determines if a sell action should be executed based on the signal and current position.

        A sell action is executed if the signal is -1 (indicating a sell signal) and the current position is
        greater than 0 (indicating that there are shares to sell).
        """
        return signal == -1 and position > 0

    def _execute_buy(
        self, cash: float, position: int, price: float, ticker: str, timestamp: pd.Timestamp
    ) -> tuple[int, float]:
        """
        Executes a buy action, updating the cash and position accordingly.
        """
        per_share_cost  = price * (1 + self.slippage + self.commission)
        shares_to_buy   = int(cash // per_share_cost)
        total_trade_cost = shares_to_buy * per_share_cost
        if shares_to_buy > 0:
            cash -= total_trade_cost
            position += shares_to_buy
            self.trade_log.append(
                TradeLogEntry(timestamp=timestamp, ticker=ticker, action=BUY, shares=shares_to_buy, price=price)
            )
        return position, cash

    def _execute_sell(
        self, cash: float, position: int, price: float, ticker: str, timestamp: pd.Timestamp
    ) -> tuple[int, float]:
        """
        Executes a sell action, updating the cash and position accordingly.
        """
        proceeds = position * price * (1 - self.commission)
        cash += proceeds
        self.trade_log.append(
            TradeLogEntry(timestamp=timestamp, ticker=ticker, action=SELL, shares=position, price=price)
        )
        position = 0
        return position, cash

    def _update_portfolio(
        self, df: pd.DataFrame, idx: int, position: int, cash: float, price: float
    ) -> None:
        """
        Updates the portfolio values in the DataFrame.
        """
        df.iat[idx, df.columns.get_loc(POSITION_COLUMN)] = position
        df.iat[idx, df.columns.get_loc(CASH_COLUMN)] = cash
        df.iat[idx, df.columns.get_loc(HOLDINGS_COLUMN)] = position * price
        df.iat[idx, df.columns.get_loc(TOTAL_VALUE_COLUMN)] = cash + (position * price)
