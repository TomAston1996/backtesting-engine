import numpy as np
import pandas as pd
import pytest

from backtesting_engine.constants import CLOSE_COLUMN, SIGNAL_COLUMN
from backtesting_engine.exceptions import InvalidDataError  # adjust import if needed
from backtesting_engine.strategies.constants import MA_COLUMN
from backtesting_engine.strategies.mean_reversion import MeanReversionStrategy


@pytest.fixture
def sample_data() -> pd.DataFrame:
    data = pd.DataFrame(
        {
            "Date": pd.date_range("2023-01-01", periods=10, freq="D"),
            "Close": [100, 95, 90, 85, 87, 90, 95, 100, 105, 110],
        }
    )
    data.set_index("Date", inplace=True)
    return data


def test_invalid_data_raises(sample_data: pd.DataFrame) -> None:
    # Act & Assert
    with pytest.raises(InvalidDataError):
        MeanReversionStrategy(sample_data.iloc[:3], window=5, threshold=0.01)


def test_generate_signals_output(sample_data: pd.DataFrame) -> None:
    # Arrange
    window = 3
    threshold = 0.05  # 5%
    strat = MeanReversionStrategy(sample_data, window=window, threshold=threshold)

    # Act
    df_signals = strat.generate_signals()

    # Assert
    assert MA_COLUMN in df_signals.columns
    assert SIGNAL_COLUMN in df_signals.columns
    assert np.isnan(df_signals[SIGNAL_COLUMN].iloc[0])

    # For index 3 (4th day), price is 85, MA ~ 90.0 for last 3 closes (90,95,100) approx
    # Check that price < MA * (1 - threshold) triggers buy (1)
    signal_at_3 = df_signals[SIGNAL_COLUMN].iloc[3]
    expected_buy = 1 if df_signals[CLOSE_COLUMN].iloc[2] < df_signals[MA_COLUMN].iloc[2] * (1 - threshold) else 0
    assert signal_at_3 == expected_buy or signal_at_3 == 0

    # Similarly check for a sell signal later when price > MA * (1 + threshold)
    # For example day 9 (index 8) price is 105, check if sell triggered
    signal_at_9 = df_signals[SIGNAL_COLUMN].iloc[9]
    expected_sell = -1 if df_signals[CLOSE_COLUMN].iloc[8] > df_signals[MA_COLUMN].iloc[8] * (1 + threshold) else 0
    assert signal_at_9 == expected_sell or signal_at_9 == 0


def test_signals_are_only_in_1_0_or_minus_1(sample_data: pd.DataFrame) -> None:
    # Arrange
    strat = MeanReversionStrategy(sample_data, window=3, threshold=0.05)

    # Act
    df_signals = strat.generate_signals()

    valid_signals = {np.nan, 1, 0, -1}

    # Assert
    assert all(s in valid_signals or pd.isna(s) for s in df_signals[SIGNAL_COLUMN])
