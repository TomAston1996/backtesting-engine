import os
import tempfile

from typing import Generator
from unittest.mock import patch

import pandas as pd
import pytest

from backtesting_engine.data.data_loader import DataLoader
from backtesting_engine.data.lru_cache import CacheKey, PersistentLRUCache


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Returns a sample dataframe with dummy stock data"""
    return pd.DataFrame(
        {
            "Open": [100, 102],
            "Close": [110, 111],
        },
        index=pd.to_datetime(["2022-01-01", "2022-01-02"]),
    )


@pytest.fixture
def multiindex_df():
    arrays = [["Open", "Close"], ["USD", "USD"]]
    tuples = list(zip(*arrays))
    columns = pd.MultiIndex.from_tuples(tuples)
    return pd.DataFrame([[100, 110], [102, 111]], columns=columns, index=pd.date_range("2022-01-01", periods=2))


@pytest.fixture
def temp_path() -> Generator[str, None, None]:
    """Creates a temporary directory for testing purposes"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def dataloader(tmp_path) -> DataLoader:
    """Returns a DataLoader with a fresh PersistentLRUCache in a temporary directory"""
    cache = PersistentLRUCache(cache_dir=tmp_path, cache_file="lru_cache.pkl", max_size=2)
    return DataLoader(cache=cache)


def test_load_from_csv_valid(temp_path, sample_df: pd.DataFrame) -> None:
    # Arrange
    csv_path = os.path.join(temp_path, "sample.csv")
    sample_df.to_csv(csv_path)
    loader = DataLoader()

    # Act
    df = loader.load(ticker="DUMMY", start_date="2022-01-01", end_date="2022-01-02", source="csv", csv_path=csv_path)

    # Assert
    pd.testing.assert_frame_equal(df, sample_df)


def test_load_from_csv_missing_path_raises() -> None:
    # Arrange
    loader = DataLoader()

    # Act & Assert
    with pytest.raises(ValueError, match="csv_path must be provided"):
        loader.load(ticker="AAPL", start_date="2022-01-01", end_date="2022-01-02", source="csv")


@patch("backtesting_engine.data.data_loader.yf.download")
def test_load_from_yfinance_cache_miss(mock_download, dataloader: DataLoader, sample_df: pd.DataFrame) -> None:
    # Arrange
    mock_download.return_value = sample_df

    # Act
    df = dataloader.load("AAPL", "2022-01-01", "2022-01-02", source="yfinance")

    # Assert
    assert dataloader.cache.has(CacheKey("AAPL", "2022-01-01", "2022-01-02"))
    pd.testing.assert_frame_equal(df, sample_df)
    mock_download.assert_called_once()


@patch("backtesting_engine.data.data_loader.yf.download")
def test_load_from_yfinance_cache_hit(mock_download, dataloader: DataLoader, sample_df: pd.DataFrame) -> None:
    # Arrange
    key = CacheKey("AAPL", "2022-01-01", "2022-01-02")
    dataloader.cache.set(key, sample_df)

    # Act
    df = dataloader.load("AAPL", "2022-01-01", "2022-01-02", source="yfinance")

    # Assert
    pd.testing.assert_frame_equal(df, sample_df)
    mock_download.assert_not_called()


def test_load_with_unknown_source_raises(dataloader: DataLoader) -> None:
    # Act & Assert
    with pytest.raises(ValueError, match="Unknown source"):
        dataloader.load("AAPL", "2022-01-01", "2022-01-02", source="unknown")


@patch("backtesting_engine.data.data_loader.yf.download")
def test_load_from_yfinance_droplevel(mock_download, dataloader: DataLoader, multiindex_df: pd.DataFrame) -> None:
    # Arrange
    mock_download.return_value = multiindex_df

    # Act
    df = dataloader.load("AAPL", "2022-01-01", "2022-01-02", source="yfinance")

    # Assert
    assert isinstance(df.columns, pd.Index)
    assert list(df.columns) == ["Open", "Close"]
    mock_download.assert_called_once()


@patch("pandas.read_csv")
def test_load_from_csv_droplevel(mock_read_csv, dataloader: DataLoader, multiindex_df: pd.DataFrame, tmp_path) -> None:
    # Arrange
    mock_read_csv.return_value = multiindex_df
    csv_path = tmp_path / "dummy.csv"

    # Act
    df = dataloader.load("IGNORED", "2022-01-01", "2022-01-02", source="csv", csv_path=str(csv_path))

    # Assert
    assert isinstance(df.columns, pd.Index)
    assert list(df.columns) == ["Open", "Close"]
    mock_read_csv.assert_called_once_with(str(csv_path), index_col=0, parse_dates=True)
