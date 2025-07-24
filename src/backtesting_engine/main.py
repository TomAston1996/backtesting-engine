from backtesting_engine.data.data_loader import load_data
from backtesting_engine.engine import BTXEngine
from backtesting_engine.interfaces import EngineContext
from backtesting_engine.strategies.sma_crossover import SMACrossoverStrategy


if __name__ == "__main__":
    TICKER = "AAPL"
    START_DATE = "2020-01-01"
    END_DATE = "2023-01-01"

    data = load_data(TICKER, START_DATE, END_DATE)

    engine = BTXEngine(
        strategy=SMACrossoverStrategy(data=data, short_window=20, long_window=50),
        context=EngineContext(
            data=data,
            initial_cash=100000.0,
            portfolio={},
            slippage=0.01,
            commission=0.001,
        ),
    )

    engine.run_backtest()
