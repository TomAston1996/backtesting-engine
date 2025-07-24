import pandas as pd
import pytest

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
from backtesting_engine.engine import BTXEngine
from backtesting_engine.interfaces import EngineContext
from backtesting_engine.strategies.interfaces import IStrategy


class MockStrategy(IStrategy):
    def __init__(self, data: pd.DataFrame) -> None:
        self.data = data

    def validate_data(self) -> None:
        pass

    def generate_signals(self) -> pd.DataFrame:
        # Return the data with signals already set
        return self.data


@pytest.fixture
def sample_data() -> pd.DataFrame:
    idx = pd.date_range("2022-01-01", periods=5, freq="D")
    columns = pd.MultiIndex.from_tuples([(CLOSE_COLUMN, "TEST"), (SIGNAL_COLUMN, "TEST")])

    data = pd.DataFrame(
        [
            [100, 0],
            [101, 1],  # Buy signal
            [102, 0],
            [103, -1],  # Sell signal
            [104, 0],
        ],
        index=idx,
        columns=columns,
    )

    return data


@pytest.fixture
def context(sample_data) -> EngineContext:
    return EngineContext(data=sample_data, initial_cash=10_000, portfolio={"TEST": 0}, slippage=0.001, commission=0.001)


def test_trades_executed_when_buy_and_sell_signals_are_present(
    context: EngineContext, sample_data: pd.DataFrame
) -> None:
    # Arrange
    strategy = MockStrategy(sample_data)
    engine = BTXEngine(strategy, context)

    # Act
    _ = engine.run_backtest()

    # Assert
    trades = engine.trade_log
    assert len(trades) == 2
    assert trades[0].action == BUY
    assert trades[1].action == SELL


def test_final_position_is_zero_after_sell(context: EngineContext, sample_data: pd.DataFrame) -> None:
    # Arrange
    strategy = MockStrategy(sample_data)
    engine = BTXEngine(strategy, context)

    # Act
    df = engine.run_backtest()

    # Assert
    final_position = df[(POSITION_COLUMN, "TEST")].iloc[-1]
    assert final_position == 0


def test_cash_after_sell_is_greater_than_initial(context: EngineContext, sample_data: pd.DataFrame) -> None:
    # Arrange
    strategy = MockStrategy(sample_data)
    engine = BTXEngine(strategy, context)

    # Act
    df = engine.run_backtest()

    # Assert
    final_cash = df[(CASH_COLUMN, "TEST")].iloc[-1]
    assert final_cash > context.initial_cash * 0.99  # account for slippage/commission


def test_holdings_should_be_zero_after_sell(context: EngineContext, sample_data: pd.DataFrame) -> None:
    # Arrange
    strategy = MockStrategy(sample_data)
    engine = BTXEngine(strategy, context)

    # Act
    df = engine.run_backtest()

    # Assert
    final_holdings = df[(HOLDINGS_COLUMN, "TEST")].iloc[-1]
    assert final_holdings == 0.0


def test_portfolio_columns_exist(context: EngineContext, sample_data: pd.DataFrame) -> None:
    # Arrange
    strategy = MockStrategy(sample_data)
    engine = BTXEngine(strategy, context)

    # Act
    df = engine.run_backtest()

    # Assert
    for col in [CASH_COLUMN, POSITION_COLUMN, HOLDINGS_COLUMN, TOTAL_VALUE_COLUMN]:
        assert (col, "TEST") in df.columns


def test_no_trade_when_no_signal(context: EngineContext, sample_data: pd.DataFrame) -> None:
    # Arrange
    no_signal_data = sample_data.copy()
    no_signal_data[(SIGNAL_COLUMN, "TEST")] = 0

    strategy = MockStrategy(no_signal_data)
    engine = BTXEngine(strategy, context)

    # Act
    df = engine.run_backtest()

    assert len(engine.trade_log) == 0
    assert all(df[(POSITION_COLUMN, "TEST")] == 0)
    assert all(df[(CASH_COLUMN, "TEST")] == context.initial_cash)
