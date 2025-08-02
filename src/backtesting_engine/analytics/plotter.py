import os

from enum import Enum

import pandas as pd
import plotly.graph_objs as go

from backtesting_engine.analytics.constants import BUY_AND_HOLD_COLUMN, DRAWDOWN_COLUMN, OUTPUT_DIR, ROLLING_MAX_COLUMN
from backtesting_engine.analytics.interfaces import IPlotGenerator
from backtesting_engine.constants import CASH_COLUMN, CLOSE_COLUMN, SIGNAL_COLUMN, TOTAL_VALUE_COLUMN
from backtesting_engine.interfaces import EngineContext


class PlotColors(Enum):
    """
    Enum to define colors used in plots.
    """

    RED = "#F3310F"
    GREEN = "#127C12"
    MINT = "#52E7A2"
    BLUE = "#95D1E5"
    GRAY = "#A9A9A9"
    LIGHT_GRAY = "#D3D3D3"
    DARK_GRAY = "#696969"
    WHITE = "#FFFFFF"
    BLACK1 = "#111111"
    BLACK2 = "#222222"


class PlotGenerator(IPlotGenerator):
    """Class to generate plots for backtesting results."""

    def __init__(self, backtest_results_df: pd.DataFrame, strategy_name: str, context: EngineContext) -> None:
        self.backtest_results_df = backtest_results_df.copy()
        self.strategy_name = strategy_name
        self.ticker = context.ticker.lower()
        self.sim_group = context.sim_group
        self.sim_id = context.sim_id
        self.x_axis_date_values = self.backtest_results_df.index.tolist()

        self._add_buy_and_hold_column()

    def _add_buy_and_hold_column(self) -> None:
        """
        Add a column for the buy-and-hold strategy value to the DataFrame.
        This is calculated as if the initial cash was invested in the stock at the start.
        """
        initial_cash = self.backtest_results_df[CASH_COLUMN].iloc[0]
        self.backtest_results_df[BUY_AND_HOLD_COLUMN] = (
            initial_cash / self.backtest_results_df[CLOSE_COLUMN].iloc[0]
        ) * self.backtest_results_df[CLOSE_COLUMN]

    def generate(self) -> None:
        """
        Generate all plots for the backtesting results and save them to the output directory.
        """
        self._generate_portfolio_value_vs_buy_and_hold_value_plot()
        self._generate_daily_returns_plot()
        self._generate_drawdown_plot()

    def _generate_portfolio_value_vs_buy_and_hold_value_plot(self) -> None:
        """
        Generate a plot of the portfolio value over time against the stock price (including buy/sell signals).

        This chart shows how the strategy performs compared to just holding the stock.
        """
        buy_signals = self.backtest_results_df[self.backtest_results_df[SIGNAL_COLUMN] == 1]
        sell_signals = self.backtest_results_df[self.backtest_results_df[SIGNAL_COLUMN] == -1]

        buy_x = buy_signals.index.tolist()
        sell_x = sell_signals.index.tolist()

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=self.x_axis_date_values,
                y=self.backtest_results_df[BUY_AND_HOLD_COLUMN],
                name="Buy & Hold Value",
                line=dict(color=PlotColors.BLUE.value),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=self.x_axis_date_values,
                y=self.backtest_results_df[TOTAL_VALUE_COLUMN],
                name="Portfolio Value",
                line=dict(color=PlotColors.MINT.value),
            )
        )

        fig.add_trace(
            go.Scatter(
                x=buy_x,
                y=buy_signals[BUY_AND_HOLD_COLUMN],
                mode="markers",
                name="Buy Signal",
                marker=dict(symbol="triangle-up", color=PlotColors.GREEN.value, size=8),
            )
        )

        fig.add_trace(
            go.Scatter(
                x=sell_x,
                y=sell_signals[BUY_AND_HOLD_COLUMN],
                mode="markers",
                name="Sell Signal",
                marker=dict(symbol="triangle-down", color=PlotColors.RED.value, size=8),
            )
        )

        self._update_background_colors_dark_mode(
            fig,
            title=f"{self.strategy_name} Portfolio vs Buy & Hold",
            xaxis_title="Date",
            yaxis_title="Hold / Portfolio Value",
        )

        self._save(fig, "strategy_vs_buy_and_hold")

    def _generate_daily_returns_plot(self) -> None:
        """
        Generate a plot of daily returns for the strategy in percentage terms.
        This shows the daily performance of the strategy.
        """
        daily_returns = self.backtest_results_df[TOTAL_VALUE_COLUMN].pct_change().dropna()

        fig = go.Figure()

        fig.add_trace(
            go.Bar(x=self.x_axis_date_values, y=daily_returns, name="Daily Returns", marker_color=PlotColors.MINT.value)
        )

        self._update_background_colors_dark_mode(
            fig,
            title=f"{self.strategy_name} Daily Returns",
            xaxis_title="Date",
            yaxis_title="Daily Returns (%)",
        )

        self._save(fig, "daily_returns")

    def _generate_drawdown_plot(self) -> None:
        """
        Generate a plot showing the drawdown of the portfolio over time.

        Running Max: Tracks the all-time high value of your portfolio.
        Portfolio Value: Your actual value over time.
        Drawdown: Visual dip from the peak — great for spotting volatility or risk.
        """
        self.backtest_results_df[ROLLING_MAX_COLUMN] = self.backtest_results_df[TOTAL_VALUE_COLUMN].cummax()
        self.backtest_results_df[DRAWDOWN_COLUMN] = (
            self.backtest_results_df[TOTAL_VALUE_COLUMN] - self.backtest_results_df[ROLLING_MAX_COLUMN]
        ) / self.backtest_results_df[ROLLING_MAX_COLUMN]

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=self.x_axis_date_values,
                y=self.backtest_results_df[TOTAL_VALUE_COLUMN],
                name="Portfolio Value",
                line=dict(color=PlotColors.LIGHT_GRAY.value, width=2, dash="dash"),
                yaxis="y1",
            )
        )

        fig.add_trace(
            go.Scatter(
                x=self.x_axis_date_values,
                y=self.backtest_results_df[DRAWDOWN_COLUMN],
                name="Drawdown",
                line=dict(color=PlotColors.RED.value),
                yaxis="y2",
            )
        )

        self._update_background_colors_dark_mode(
            fig,
            title=f"{self.strategy_name} Drawdown Over Time",
            xaxis_title="Date",
            yaxis_title="Value / Drawdown",
        )

        fig.update_layout(
            yaxis=dict(
                title="Portfolio Value",
                side="left",
                showgrid=False,
                zeroline=False
            ),
            yaxis2=dict(
                title="Drawdown (%)",
                side="right",
                overlaying="y",
                tickformat=".0%",
                showgrid=False,
                zeroline=False
            ),
            margin=dict(t=60, b=40),
            xaxis=dict(zeroline=False, showline=False)
        )

        self._save(fig, "drawdown")

    def _save(self, fig: go.Figure, filename: str) -> None:
        """
        Save the plot to the structured output directory: out/<sim_group>/<ticker>_<filename>.png
        """
        sim_dir = os.path.join(OUTPUT_DIR, self.sim_group, self.ticker)
        os.makedirs(sim_dir, exist_ok=True)

        filename = f"{self.sim_id}_{self.strategy_name.lower()}_{filename}.png"
        png_path = os.path.join(sim_dir, filename)

        fig.write_image(png_path, width=1200, height=800)

    def _update_background_colors_dark_mode(
        self, fig: go.Figure, title: str, xaxis_title: str, yaxis_title: str
    ) -> None:
        """
        Update the background colors of the plot to match the dark theme.
        """
        fig.update_layout(
            title=title,
            xaxis_title=xaxis_title,
            yaxis_title=yaxis_title,
            paper_bgcolor=PlotColors.BLACK2.value,
            plot_bgcolor=PlotColors.BLACK1.value,
            font=dict(color=PlotColors.WHITE.value),
            xaxis=dict(
                gridcolor=PlotColors.GRAY.value,
                # zerolinecolor=PlotColors.GRAY.value,
                linecolor=PlotColors.GRAY.value,
                tickcolor=PlotColors.GRAY.value,
            ),
            yaxis=dict(
                gridcolor=PlotColors.GRAY.value,
                zerolinecolor=PlotColors.GRAY.value,
                linecolor=PlotColors.GRAY.value,
                tickcolor=PlotColors.GRAY.value,
            ),
        )
