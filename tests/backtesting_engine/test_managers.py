import json

from pathlib import Path

import pytest

from backtesting_engine.interfaces import SimItem
from backtesting_engine.managers import QueueManager


@pytest.fixture
def sample_queue_file(tmp_path: Path) -> Path:
    queue_file = tmp_path / "queue.json"
    config = {
        "sim_group": "test_group",
        "output_dir_location": str(tmp_path / "output"),
        "author": "tester",
        "sims": [
            {
                "sim_id": "sim1",
                "strategy": {"type": "buy_and_hold", "fields": {}},
                "data": {
                    "ticker": "AAPL",
                    "start_date": "2020-01-01",
                    "end_date": "2020-12-31",
                    "source": "yahoo",
                },
                "sim_config": {"initial_cash": 1000, "slippage": 0.0, "commission": 0.0},
            }
        ],
    }
    queue_file.write_text(json.dumps(config))
    return queue_file


def test_load_queue_config(sample_queue_file: Path) -> None:
    # Arrange
    qm = QueueManager(str(sample_queue_file), max_workers=1)

    # Act & Assert
    assert qm.queue_config.sim_group == "test_group"
    assert qm.queue_config.author == "tester"
    assert isinstance(qm.queue_config.sims[0], SimItem)
    assert qm.queue_config.sims[0].data.ticker == "AAPL"


def test_create_output_directory(sample_queue_file: Path) -> None:
    # Arrange
    qm = QueueManager(str(sample_queue_file), max_workers=1)

    # Act
    output_dir = Path(qm.queue_config.output_dir_location)

    # Assert
    assert output_dir.exists()
    assert output_dir.is_dir()
