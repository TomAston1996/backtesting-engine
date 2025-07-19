# 📈 backtesting-engine

A simple, extensible Python backtesting engine for evaluating trading strategies on historical market data.

---

## 🧠 Background: What is Backtesting?

**Backtesting** is the process of evaluating a trading strategy using historical price data to simulate how it would have performed in the past. It helps quantify the effectiveness, risk, and robustness of an strategy before deploying it with real capital.

By simulating trades over time, backtesting allows quants and traders to:
- Validate strategy logic (e.g. moving average crossover, momentum, mean reversion)
- Estimate historical returns, drawdowns, and volatility
- Compare strategies using objective metrics like Sharpe Ratio or Win Rate
- Test the impact of transaction costs and slippage
- Avoid overfitting through walk-forward analysis or out-of-sample testing

Backtesting is a core building block of quantitative finance and algorithmic trading.

---

## 🚀 Project Goals

This project aims to provide:

- ✅ A clean, testable Python backtesting engine
- ✅ Strategy logic separated from execution & portfolio simulation
- ✅ Support for custom indicators and strategies (plug-and-play)
- ✅ Simple performance reporting (e.g. equity curve, returns, drawdown)
- ✅ Minimal dependencies (built on `pandas`, `matplotlib`, etc.)

Eventually, the engine can be extended to:
- Support multiple assets or portfolios
- Model execution latency, slippage, and fees
- Run walk-forward or Monte Carlo simulations
- Integrate with real-time paper trading APIs

---

## 📦 Getting Started

```bash
# install dependencies with uv
uv sync

# run the strategy
uv run python main.py