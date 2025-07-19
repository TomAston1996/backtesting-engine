import pandas as pd
import pytest
from src.strategies.sma_crossover import SMACrossoverStrategy
from src.strategies.exceptions import InvalidDataError


@pytest.fixture
def dummy_data():
    return pd.DataFrame({
        'Close': [100, 102, 104, 103, 105, 107, 106, 108, 110, 112]
    })


def test_valid_strategy_generates_signals(dummy_data) -> None:
    # Arrange
    strategy = SMACrossoverStrategy(data=dummy_data, short_window=3, long_window=5)

    # Act
    result = strategy.generate_signals()

    # Assert
    assert isinstance(result, pd.DataFrame)
    assert 'Signal' in result.columns
    assert 'Short_MA' in result.columns
    assert 'Long_MA' in result.columns
    assert result['Signal'].iloc[-1] in [-1, 0, 1] # The signal column should have values in [-1, 0, 1] and be shifted
    assert pd.isna(result['Signal'].iloc[0])  # shifted, so 1st signal should be NaN


def test_invalid_data_type_raises_error() -> None:
    with pytest.raises(InvalidDataError, match="Data must be a pandas DataFrame."):
        SMACrossoverStrategy(data="not a df", short_window=3, long_window=5)


def test_missing_close_column_raises_error() -> None:
    df = pd.DataFrame({'Open': [1, 2, 3]})
    with pytest.raises(InvalidDataError, match="must contain a 'Close' column"):
        SMACrossoverStrategy(data=df, short_window=3, long_window=5)


def test_empty_dataframe_raises_error() -> None:
    df = pd.DataFrame(columns=["Close"])
    with pytest.raises(InvalidDataError, match="cannot be empty"):
        SMACrossoverStrategy(data=df, short_window=3, long_window=5)


def test_too_short_data_raises_error() -> None:
    df = pd.DataFrame({'Close': [100, 101]})
    with pytest.raises(InvalidDataError, match="Data length must be greater"):
        SMACrossoverStrategy(data=df, short_window=3, long_window=5)