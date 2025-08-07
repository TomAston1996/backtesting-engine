import pandas as pd
import pytest

from backtesting_engine.constants import SIGNAL_COLUMN
from backtesting_engine.strategies.buy_and_hold import BuyAndHoldStrategy


@pytest.fixture
def sample_data() -> pd.DataFrame:
    data = pd.DataFrame(
        {
            "Date": pd.date_range(start="2023-01-01", periods=5, freq="D"),
            "Open": [100, 102, 101, 105, 107],
            "High": [102, 103, 104, 108, 109],
            "Low": [99, 100, 100, 104, 106],
            "Close": [101, 102, 103, 107, 108],
            "Volume": [1000, 1100, 1200, 1300, 1250],
        }
    )
    data.set_index("Date", inplace=True)
    return data


def test_buy_and_hold_signals(sample_data: pd.DataFrame) -> None:
    # Arrange
    strat = BuyAndHoldStrategy(data=sample_data)

    # Act
    signals = strat.generate_signals()[SIGNAL_COLUMN]

    # Assert
    assert all(s == 1 for s in signals.iloc[1:]), "All following signals should be hold"
