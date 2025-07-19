from src.data.data_loader import load_data
from src.backtesting_engine.engine import BTXEngine
from src.strategies.sma_crossover import SMACrossoverStrategy


if __name__ == "__main__":
    TICKER = "AAPL"
    START_DATE = "2020-01-01"
    END_DATE = "2023-01-01"

    data = load_data(TICKER, START_DATE, END_DATE)

    strategy = SMACrossoverStrategy(data=data, short_window=20, long_window=50)

    engine = BTXEngine(data=data, strategy=strategy)

    engine.run_backtest()
