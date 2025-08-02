import os

import pandas as pd
import plotly.graph_objs as go

from backtesting_engine.analytics.constants import OUTPUT_DIR
from backtesting_engine.analytics.interfaces import IPlotGenerator
from backtesting_engine.constants import CASH_COLUMN, CLOSE_COLUMN, SIGNAL_COLUMN, TOTAL_VALUE_COLUMN
from backtesting_engine.interfaces import EngineContext


class PlotGenerator(IPlotGenerator):
    """Class to generate plots for backtesting results."""

    def __init__(self, backtest_results_df: pd.DataFrame, strategy_name: str, context: EngineContext) -> None:
        self.backtest_results_df = backtest_results_df.copy()
        self.strategy_name = strategy_name
        self.ticker = context.ticker.lower()
        self.sim_group = context.sim_group
        self.sim_id = context.sim_id

        self.X_AXIS_DATE = "AxisDate"
        self.backtest_results_df[self.X_AXIS_DATE] = pd.to_datetime(self.backtest_results_df.index)
        self.backtest_results_df.dropna(subset=[self.X_AXIS_DATE], inplace=True)
        self.x_values = self.backtest_results_df[self.X_AXIS_DATE].tolist()

        self._add_buy_and_hold_column()

    def _add_buy_and_hold_column(self) -> None:
        """
        Add a column for the buy-and-hold strategy value to the DataFrame.
        This is calculated as if the initial cash was invested in the stock at the start.
        """
        initial_cash = self.backtest_results_df[CASH_COLUMN].iloc[0]
        self.backtest_results_df["buy_and_hold_value"] = (
            initial_cash / self.backtest_results_df[CLOSE_COLUMN].iloc[0]
        ) * self.backtest_results_df[CLOSE_COLUMN]

    def generate(self) -> None:
        """
        Generate all plots for the backtesting results and save them to the output directory.
        """
        self._generate_portfolio_value_plot()

    def _generate_portfolio_value_plot(self) -> None:
        """
        Generate a plot of the portfolio value over time against the stock price (including buy/sell signals).

        This chart shows how the strategy performs compared to just holding the stock.
        """
        buy_signals = self.backtest_results_df[self.backtest_results_df[SIGNAL_COLUMN] == 1]
        sell_signals = self.backtest_results_df[self.backtest_results_df[SIGNAL_COLUMN] == -1]

        buy_x = buy_signals[self.X_AXIS_DATE].tolist()
        sell_x = sell_signals[self.X_AXIS_DATE].tolist()

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=self.x_values,
                y=self.backtest_results_df["buy_and_hold_value"],
                name="Buy & Hold Value",
                line=dict(color="#95D1E5"),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=self.x_values,
                y=self.backtest_results_df[TOTAL_VALUE_COLUMN],
                name="Portfolio Value",
                line=dict(color="#52E7A2"),
            )
        )

        fig.add_trace(
            go.Scatter(
                x=buy_x,
                y=buy_signals["buy_and_hold_value"],
                mode="markers",
                name="Buy Signal",
                marker=dict(symbol="triangle-up", color="green", size=8),
            )
        )

        fig.add_trace(
            go.Scatter(
                x=sell_x,
                y=sell_signals["buy_and_hold_value"],
                mode="markers",
                name="Sell Signal",
                marker=dict(symbol="triangle-down", color="red", size=8),
            )
        )

        self._update_background_colors_dark_mode(
            fig,
            title=f"{self.strategy_name} Portfolio vs Buy & Hold",
            xaxis_title="Date",
            yaxis_title="Hold / Portfolio Value",
        )

        self._save(fig, "strategy_vs_buy_and_hold")

    def _save(self, fig: go.Figure, filename: str) -> None:
        """
        Save the plot to the structured output directory: out/<sim_group>/<ticker>_<filename>.png
        """
        sim_dir = os.path.join(OUTPUT_DIR, self.sim_group, self.ticker)
        os.makedirs(sim_dir, exist_ok=True)

        filename = f"{self.sim_id}_{self.strategy_name.lower()}_{filename}.png"
        png_path = os.path.join(sim_dir, filename)

        fig.write_image(png_path, width=1200, height=800)


    def _update_background_colors_dark_mode(self, fig: go.Figure, title: str, xaxis_title: str, yaxis_title: str) -> None:
        """
        Update the background colors of the plot to match the dark theme.
        """
        fig.update_layout(
            title=title,
            xaxis_title=xaxis_title,
            yaxis_title=yaxis_title,
            paper_bgcolor="#222222",
            plot_bgcolor="#111111",
            font=dict(color="white"),

            xaxis=dict(
                gridcolor="gray",
                zerolinecolor="gray",
                linecolor="gray",
                tickcolor="gray",
            ),
            yaxis=dict(
                gridcolor="gray",
                zerolinecolor="gray",
                linecolor="gray",
                tickcolor="gray",
            ),
        )
