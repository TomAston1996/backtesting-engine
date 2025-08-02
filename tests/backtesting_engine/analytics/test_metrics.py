import pandas as pd

from backtesting_engine.analytics.interfaces import BacktestMetrics
from backtesting_engine.analytics.metrics import BacktestMetricCreator
from backtesting_engine.constants import TOTAL_VALUE_COLUMN


FAKE_TICKER = "TEST"


def generate_fake_portfolio_df() -> pd.DataFrame:
    data = {TOTAL_VALUE_COLUMN: [100, 105, 102, 108, 110]}
    idx = pd.date_range(start="2022-01-01", periods=5, freq="D")
    return pd.DataFrame(data, index=idx)


test_metrics = BacktestMetricCreator(backtest_results_df=generate_fake_portfolio_df(), ticker=FAKE_TICKER)


def test_total_return() -> None:
    assert round(test_metrics.get_total_return(), 4) == 0.10  # (110/100 - 1) shows 10% return


def test_sharpe_ratio() -> None:
    sharpe = test_metrics.get_sharpe_ratio()
    assert isinstance(sharpe, float)
    assert sharpe > 0


def test_max_drawdown() -> None:
    max_dd = test_metrics.get_max_drawdown()
    assert round(max_dd, 4) == -0.0286  # (102 - 105) / 105


def test_volatility() -> None:
    vol = test_metrics.get_volatility()
    assert isinstance(vol, float)
    assert vol > 0


def test_get_backtest_metrics() -> None:
    result = test_metrics.get_backtest_metrics()
    assert isinstance(result, BacktestMetrics)
    assert result.total_return == test_metrics.get_total_return()
    assert result.sharpe_ratio == test_metrics.get_sharpe_ratio()
    assert result.max_drawdown == test_metrics.get_max_drawdown()
    assert result.volatility == test_metrics.get_volatility()
