"""
This module implements the backtesting engine for executing trading strategies.
"""

from typing import Callable

import pandas as pd

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
from backtesting_engine.interfaces import EngineConfig, EngineContext, IMetricsCreator, TradeLogEntry


class BTXEngine:
    """
    BTXEngine is the core backtesting engine that executes trading strategies. It processes
    the strategy signals and updates the portfolio accordingly. It can handle multiple tickers
    and maintains a trade log for all executed trades.
    """

    def __init__(self, config: EngineConfig, context: EngineContext) -> None:
        # inject dependencies
        self.strategy = context.strategy
        self.data = context.data.copy()
        self.portfolio = context.portfolio.copy()

        # metrics creator should be called after the backtest is run
        # to ensure it has the complete backtest results DataFrame
        self.metrics_creator: Callable[[pd.DataFrame, str], IMetricsCreator] = context.metrics_creator

        # config parameters
        self.initial_cash = config.initial_cash
        self.slippage = config.slippage
        self.commission = config.commission

        self.trade_log: list[TradeLogEntry] = []

    def run_backtest(self) -> pd.DataFrame:
        """
        Run main backtest loop.
        """
        df = self.strategy.generate_signals()

        for ticker in self.portfolio.keys():
            df = self._backtest_single_ticker(df, ticker)

        self.data = df
        print(self.data.head())  # Display the first few rows of the backtested data
        return df

    def _backtest_single_ticker(self, df: pd.DataFrame, ticker: str) -> pd.DataFrame:
        """
        Backtest a single ticker using the strategy signals.

        This method updates the DataFrame with trading signals and portfolio values.
        """
        price_col = (CLOSE_COLUMN, ticker)
        signal_col = (SIGNAL_COLUMN, ticker)

        # Initialize portfolio columns
        df[(CASH_COLUMN, ticker)] = float(self.initial_cash)
        df[(POSITION_COLUMN, ticker)] = 0
        df[(HOLDINGS_COLUMN, ticker)] = 0.0
        df[(TOTAL_VALUE_COLUMN, ticker)] = 0.0

        position = 0
        cash = self.initial_cash

        for i in range(1, len(df)):
            price = df.iloc[i][price_col]
            signal = df.iloc[i][signal_col]

            if pd.isna(signal) or pd.isna(price):
                continue

            if self._should_buy(signal, position):
                position, cash = self._execute_buy(cash, position, price, ticker, df.index[i])

            elif self._should_sell(signal, position):
                position, cash = self._execute_sell(cash, position, price, ticker, df.index[i])

            self._update_portfolio(df, i, ticker, position, cash, price)

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
        shares_to_buy = cash // (price * (1 + self.slippage))
        cost = shares_to_buy * price * (1 + self.slippage + self.commission)
        if shares_to_buy > 0:
            cash -= cost
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
        proceeds = position * price * (1 - self.slippage - self.commission)
        cash += proceeds
        self.trade_log.append(
            TradeLogEntry(timestamp=timestamp, ticker=ticker, action=SELL, shares=position, price=price)
        )
        position = 0
        return position, cash

    def _update_portfolio(
        self, df: pd.DataFrame, idx: int, ticker: str, position: int, cash: float, price: float
    ) -> None:
        """
        Updates the portfolio values in the DataFrame.
        """
        df.iat[idx, df.columns.get_loc((POSITION_COLUMN, ticker))] = position
        df.iat[idx, df.columns.get_loc((CASH_COLUMN, ticker))] = cash
        df.iat[idx, df.columns.get_loc((HOLDINGS_COLUMN, ticker))] = position * price
        df.iat[idx, df.columns.get_loc((TOTAL_VALUE_COLUMN, ticker))] = cash + (position * price)
