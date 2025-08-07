import pandas as pd
import pytest

from backtesting_engine.constants import CLOSE_COLUMN, SIGNAL_COLUMN
from backtesting_engine.exceptions import InvalidDataError
from backtesting_engine.strategies.constants import MOMENTUM_COLUMN
from backtesting_engine.strategies.momentum import MomentumStrategy


@pytest.fixture
def sample_data() -> pd.DataFrame:
    data = pd.DataFrame({
        "Date": pd.date_range("2023-01-01", periods=10, freq="D"),
        CLOSE_COLUMN: [100, 102, 105, 108, 110, 112, 115, 117, 120, 123],
    })
    data.set_index("Date", inplace=True)
    return data

def test_invalid_data_raises(sample_data: pd.DataFrame) -> None:
    # Act & Assert
    with pytest.raises(InvalidDataError):
        MomentumStrategy(sample_data.iloc[:3], window=5, threshold=0.01)

def test_generate_signals(sample_data: pd.DataFrame) -> None:
    # Arrange
    window = 3
    threshold = 0.02  # 2%
    strat = MomentumStrategy(sample_data, window=window, threshold=threshold)

    # Act
    df = strat.generate_signals()

    # Assert
    assert MOMENTUM_COLUMN in df.columns
    assert SIGNAL_COLUMN in df.columns
    assert pd.isna(df[SIGNAL_COLUMN].iloc[0])

    expected_signal = 1
    assert all(signal == expected_signal or pd.isna(signal) for signal in df[SIGNAL_COLUMN].iloc[window+1:]), "Signals should mostly be buy (1)"

def test_signals_values(sample_data: pd.DataFrame) -> None:
    # Arrange
    window = 3
    threshold = 0.05
    strat = MomentumStrategy(sample_data, window=window, threshold=threshold)

    # Act
    df = strat.generate_signals()

    # Assert
    # Signals should only be in {-1, 0, 1} or NaN (due to shift)
    valid_signals = {1, 0, -1}
    assert all(s in valid_signals or pd.isna(s) for s in df[SIGNAL_COLUMN])
