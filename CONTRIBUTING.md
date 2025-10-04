# 🤝 Contributing to Backtesting Engine

Thanks for your interest in contributing! 🎉
This project simulates trading strategies on historical market data — all improvements, bug fixes, and ideas are welcome.

---

## 🛠 Setup

1. Fork and clone the repo:
 ```bash
 git clone https://github.com/TomAston1996/backtesting-engine.git
 cd backtesting-engine
 ```

2. Create a new branch:

  ```bash
  git checkout -b feat/my-feature
  ```


3. Install dependencies:

  ```bash
  uv venv
  uv sync
  ```


## 🧩 Development

Run tests and lint checks before committing:

``` bash
invoke test
invoke lint
```


## 💬 Commits

Use Conventional Commits:

```
feat: add momentum strategy
fix: correct drawdown calculation
docs: update README
```
