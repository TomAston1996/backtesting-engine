[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

# 📈 Quant Trading Backtesting Engine

A simple, extensible Python backtesting engine for evaluating trading strategies on historical market data.

## 🧑‍💻 Tech Stack

![Python]
![Pandas]
![NumPy]
![Plotly]


## ToDo

- Incorperate multiproccessing so that simualtions can run in parralel (imput JSON)
- Add lightweight visualisation - plotly graphs
- Add different ways to load data maybe a DataLoader class i.e. via yfinance or CSV
- Add caching to data loader class
- Add more strategies


## Done

- Persistance LRU cache created for more efficient data loading (perform performance tests on caching)



## Background: What is Backtesting?

**Backtesting** is the process of evaluating a trading strategy using historical price data to simulate how it would have performed in the past. It helps quantify the effectiveness, risk, and robustness of an strategy before deploying it with real capital.

By simulating trades over time, backtesting allows quants and traders to:
- Validate strategy logic (e.g. moving average crossover, momentum, mean reversion)
- Estimate historical returns, drawdowns, and volatility
- Compare strategies using objective metrics like Sharpe Ratio or Win Rate
- Test the impact of transaction costs and slippage
- Avoid overfitting through walk-forward analysis or out-of-sample testing

## 📦 Getting Started

```bash
# install dependencies with uv
make install

# run the strategy
uv run python src/backtest_engine/main.py
```

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/TomAston1996/backtesting-engine.svg?style=for-the-badge
[contributors-url]: https://github.com/TomAston1996/backtesting-engine/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/TomAston1996/backtesting-engine.svg?style=for-the-badge
[forks-url]: https://github.com/TomAston1996/backtesting-engine/network/members
[stars-shield]: https://img.shields.io/github/stars/TomAston1996/backtesting-engine.svg?style=for-the-badge
[stars-url]: https://github.com/TomAston1996/backtesting-engine/stargazers
[issues-shield]: https://img.shields.io/github/issues/TomAston1996/backtesting-engine.svg?style=for-the-badge
[issues-url]: https://github.com/TomAston1996/backtesting-engine/issues
[license-shield]: https://img.shields.io/github/license/TomAston1996/backtesting-engine.svg?style=for-the-badge
[license-url]: https://github.com/TomAston1996/backtesting-engine/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/tomaston96
[Python]: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54
[Pandas]: https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white
[AWS]: https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white
[Docker]: https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white
[FastAPI]: https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi
[Raspberry Pi]: https://img.shields.io/badge/-Raspberry_Pi-C51A4A?style=for-the-badge&logo=Raspberry-Pi
[NumPy]: https://img.shields.io/badge/numpy-%23013243.svg?style=for-the-badge&logo=numpy&logoColor=white
[Plotly]: https://img.shields.io/badge/Plotly-%233F4F75.svg?style=for-the-badge&logo=plotly&logoColor=white
