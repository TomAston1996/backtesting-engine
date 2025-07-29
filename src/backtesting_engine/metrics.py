"""
This module contains the BacktestMetricCreator class, which is used to calculate
various backtesting metrics for a portfolio, such as total return, Sharpe ratio,
"""

import pandas as pd

from backtesting_engine.constants import TOTAL_VALUE_COLUMN
from backtesting_engine.interfaces import BacktestMetrics, IMetricsCreator


class BacktestMetricCreator(IMetricsCreator):
    """Class to calculate various backtesting metrics for a portfolio.

    This class provides methods to calculate total return, Sharpe ratio, and
    maximum drawdown based on the portfolio value over time.
    """

    # TODO: Make these configurable
    PERIODS_PER_YEAR: int = 252  # Typical number of trading days in a year
    RISK_FREE_RATE: float = 0.0  # Default risk-free rate for Sharpe ratio calculation

    def __init__(self, backtest_results_df: pd.DataFrame, ticker: str) -> None:
        self.ticker = ticker
        self.portfolio_value: pd.Series = backtest_results_df.loc[:, TOTAL_VALUE_COLUMN].copy()

    def get_total_return(self) -> float:
        """
        Calculate the total return of a portfolio.

        This is the percentage change from the initial value to the final value.
        """
        return (self.portfolio_value.iloc[-1] / self.portfolio_value.iloc[0]) - 1

    def _get_daily_return_series(self) -> pd.Series:
        """
        Calculate daily returns of the portfolio.

        This is the percentage change of the portfolio value from one day to the next.
        """
        return self.portfolio_value.copy().pct_change().dropna()

    def get_sharpe_ratio(self) -> float:
        """Annualized Sharpe ratio assuming daily returns."""
        returns = self._get_daily_return_series()
        excess_returns = returns - (self.RISK_FREE_RATE / self.PERIODS_PER_YEAR)

        std = excess_returns.std()
        if std == 0 or pd.isna(std):
            return 0.0

        return (excess_returns.mean() / std) * (self.PERIODS_PER_YEAR**0.5)

    def get_max_drawdown(self) -> float:
        """
        Calculate the maximum drawdown of the portfolio.

        This is the maximum observed loss from a peak to a trough of a portfolio,
        before a new peak is achieved.
        """
        cumulative_max = self.portfolio_value.copy().cummax()
        drawdown = (self.portfolio_value.copy() - cumulative_max) / cumulative_max

        return drawdown.min()

    def get_volatility(self) -> float:
        """
        Calculate the annualized volatility of the portfolio returns.

        This is the standard deviation of daily returns, annualized.
        """
        return self._get_daily_return_series().std() * (self.PERIODS_PER_YEAR**0.5)

    def get_backtest_metrics(self) -> BacktestMetrics:
        """
        Get a BacktestMetrics data object containing total return, Sharpe ratio, and max drawdown.
        """
        return BacktestMetrics(
            ticker=self.ticker,
            total_return=self.get_total_return(),
            sharpe_ratio=self.get_sharpe_ratio(),
            max_drawdown=self.get_max_drawdown(),
            volatility=self.get_volatility(),
        )
