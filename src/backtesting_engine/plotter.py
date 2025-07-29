# import matplotlib.pyplot as plt
# import pandas as pd


# def plot_backtest_results(portfolio_value: pd.Series, data: pd.DataFrame, ticker: str = "Asset"):
#     fig, ax1 = plt.subplots(figsize=(12, 6))

#     # Plot portfolio value
#     ax1.set_title(f"Backtest Results for {ticker}")
#     ax1.plot(portfolio_value.index, portfolio_value.values, label="Portfolio Value", color="tab:blue")
#     ax1.set_ylabel("Portfolio Value", color="tab:blue")
#     ax1.tick_params(axis="y", labelcolor="tab:blue")
#     ax1.grid(True, which="both", linestyle="--", alpha=0.3)

#     # Plot price with buy/sell signals
#     ax2 = ax1.twinx()
#     ax2.plot(data.index, data["Close"], label="Price", color="gray", alpha=0.4)

#     buy_signals = data[data["Signal"] == 1]
#     sell_signals = data[data["Signal"] == -1]

#     ax2.scatter(buy_signals.index, buy_signals["Close"], marker="^", color="green", label="Buy Signal", zorder=5)
#     ax2.scatter(sell_signals.index, sell_signals["Close"], marker="v", color="red", label="Sell Signal", zorder=5)

#     ax2.set_ylabel("Price", color="gray")
#     ax2.tick_params(axis="y", labelcolor="gray")

#     # Legends
#     lines_1, labels_1 = ax1.get_legend_handles_labels()
#     lines_2, labels_2 = ax2.get_legend_handles_labels()
#     ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc="upper left")

#     plt.tight_layout()
#     plt.show()
