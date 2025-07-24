"""
This module implements the backtesting engine for executing trading strategies.
"""

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
from backtesting_engine.interfaces import EngineContext, TradeLogEntry
from backtesting_engine.strategies.interfaces import IStrategy


class BTXEngine:
    def __init__(self, strategy: IStrategy, context: EngineContext) -> None:
        self.strategy = strategy
        self.data = context.data.copy()
        self.initial_cash = context.initial_cash
        self.portfolio = context.portfolio.copy()
        self.slippage = context.slippage
        self.commission = context.commission

        self.trade_log: list[TradeLogEntry] = []

    def run_backtest(self) -> None:
        """
        Run the backtest using the provided strategy and context.
        """
        df = self.strategy.generate_signals()

        for ticker in self.portfolio.keys():
            df = self._backtest_single_ticker(df, ticker)

        self.data = df
        print(self.data.head())  # Display the first few rows of the backtested data
        return df

    def _backtest_single_ticker(self, df: pd.DataFrame, ticker: str) -> pd.DataFrame:
        price_col = (CLOSE_COLUMN, ticker)
        signal_col = (SIGNAL_COLUMN, ticker)

        # Initialize portfolio columns
        df[(CASH_COLUMN, ticker)] = self.initial_cash
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
        return signal == 1 and position == 0

    def _should_sell(self, signal: float, position: int) -> bool:
        return signal == -1 and position > 0

    def _execute_buy(
        self, cash: float, position: int, price: float, ticker: str, timestamp: pd.Timestamp
    ) -> tuple[int, float]:
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
        df.iat[idx, df.columns.get_loc((POSITION_COLUMN, ticker))] = position
        df.iat[idx, df.columns.get_loc((CASH_COLUMN, ticker))] = cash
        df.iat[idx, df.columns.get_loc((HOLDINGS_COLUMN, ticker))] = position * price
        df.iat[idx, df.columns.get_loc((TOTAL_VALUE_COLUMN, ticker))] = cash + (position * price)
