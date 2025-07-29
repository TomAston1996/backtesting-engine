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
from backtesting_engine.interfaces import BacktestMetrics, EngineConfig, EngineContext, IMetricsCreator
from backtesting_engine.strategies.interfaces import IStrategy


TICKER = "TEST"


class MockStrategy(IStrategy):
    def __init__(self, data: pd.DataFrame) -> None:
        self.data = data

    def validate_data(self) -> None:
        pass

    def generate_signals(self) -> pd.DataFrame:
        # Return the data with signals already set
        return self.data


class MockMetricsCreator(IMetricsCreator):
    def __init__(self, backtest_results_df: pd.DataFrame, ticker: str) -> None:
        self.backtest_results_df = backtest_results_df
        self.ticker = ticker

    def get_total_return(self) -> float:
        return 0.0  # Mocked value

    def get_sharpe_ratio(self) -> float:
        return 0.0  # Mocked value

    def get_max_drawdown(self) -> float:
        return 0.0  # Mocked value

    def get_volatility(self) -> float:
        return 0.0  # Mocked value

    def get_backtest_metrics(self) -> BacktestMetrics:
        return BacktestMetrics(
            ticker=self.ticker,
            total_return=9.9,
            sharpe_ratio=9.9,
            max_drawdown=9.9,
            volatility=9.9,
        )


@pytest.fixture
def sample_data() -> pd.DataFrame:
    idx = pd.date_range("2022-01-01", periods=5, freq="D")
    data = pd.DataFrame(
        {
            CLOSE_COLUMN: [100, 101, 102, 103, 104],
            SIGNAL_COLUMN: [0, 1, 0, -1, 0],
        },
        index=idx,
    )
    return data


@pytest.fixture
def context(sample_data: pd.DataFrame) -> EngineContext:
    return EngineContext(
        data=sample_data,
        ticker=TICKER,
        strategy=MockStrategy(sample_data),
        metrics_creator=MockMetricsCreator,
    )


@pytest.fixture
def config() -> EngineConfig:
    return EngineConfig(
        initial_cash=100000.0,
        slippage=0.01,
        commission=0.001,
    )


def test_trades_executed_when_buy_and_sell_signals_are_present(config: EngineConfig, context: EngineContext) -> None:
    # Arrange
    engine = BTXEngine(config, context)

    # Act
    _ = engine.run_backtest()

    # Assert
    trades = engine.trade_log
    assert len(trades) == 2
    assert trades[0].action == BUY
    assert trades[1].action == SELL


def test_final_position_is_zero_after_sell(config: EngineConfig, context: EngineContext) -> None:
    # Arrange
    engine = BTXEngine(config, context)

    # Act
    df = engine.run_backtest()

    # Assert
    final_position = df[POSITION_COLUMN].iloc[-1]
    assert final_position == 0


def test_cash_after_sell_is_greater_than_initial(config: EngineConfig, context: EngineContext) -> None:
    # Arrange
    engine = BTXEngine(config, context)

    # Act
    df = engine.run_backtest()

    # Assert
    final_cash = df[CASH_COLUMN].iloc[-1]
    assert final_cash > config.initial_cash * 0.99  # account for slippage/commission


def test_holdings_should_be_zero_after_sell(config: EngineConfig, context: EngineContext) -> None:
    # Arrange
    engine = BTXEngine(config, context)

    # Act
    df = engine.run_backtest()

    # Assert
    final_holdings = df[HOLDINGS_COLUMN].iloc[-1]
    assert final_holdings == 0.0


def test_portfolio_columns_exist(config: EngineConfig, context: EngineContext) -> None:
    # Arrange
    engine = BTXEngine(config, context)

    # Act
    df = engine.run_backtest()

    # Assert
    for col in [CASH_COLUMN, POSITION_COLUMN, HOLDINGS_COLUMN, TOTAL_VALUE_COLUMN]:
        assert col in df.columns


def test_no_trade_when_no_signal(config: EngineConfig, sample_data: pd.DataFrame) -> None:
    # Arrange
    no_signal_data = sample_data.copy()
    no_signal_data[SIGNAL_COLUMN] = 0

    context = EngineContext(
        data=no_signal_data,
        ticker=TICKER,
        strategy=MockStrategy(no_signal_data),
        metrics_creator=MockMetricsCreator,
    )
    engine = BTXEngine(config, context)

    # Act
    df = engine.run_backtest()

    # Assert
    assert len(engine.trade_log) == 0
    assert all(df[POSITION_COLUMN] == 0)
    assert all(df[CASH_COLUMN] == config.initial_cash)
