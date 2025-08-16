"""
Script to generate a test queue file for performance testing simulations.

Change the number of simulations to generate by modifying the `NUM_SIMS_TO_GENERATE` constant. This script creates a JSON file
with a specified number of simulations, each configured with a sample strategy and data parameters. The generated file can be used
to test the performance of the backtesting engine with multiple simulations.

Note: each simulation is a copy of the same strategy and data configuration, which is intended for testing purposes. You can modify
the `sim_template` to change the strategy or data parameters as needed.
"""

import json
import os

from typing import Any


NUM_SIMS_TO_GENERATE = 300
OUTPUT_DIR_LOCATION = "data/performance_test_files/"

sim_template = {
    "strategy": {"type": "sma_crossover", "fields": {"short_window": 50, "long_window": 100}},
    "data": {"source": "yfinance", "ticker": "AAPL", "start_date": "2020-01-02", "end_date": "2023-01-01"},
    "sim_config": {"initial_cash": 100000, "slippage": 0.01, "commission": 0.001},
}


def generate_test_queue_file() -> None:
    os.makedirs(OUTPUT_DIR_LOCATION, exist_ok=True)

    sims: list[dict[str, Any]] = []
    for i in range(1, NUM_SIMS_TO_GENERATE + 1):
        sim: dict[str, Any] = sim_template.copy()
        sim["sim_id"] = f"{i:03d}"  # Format sim_id with leading zeros
        sims.append(sim)

    data = {"sim_group": "example_sim_group", "output_dir_location": "./out", "author": "Tom Aston", "sims": sims}

    file_name = f"test_queue_file_{NUM_SIMS_TO_GENERATE}_sims.json"
    file_path = os.path.join(OUTPUT_DIR_LOCATION, file_name)

    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

    print(f"Generated {file_name} with {NUM_SIMS_TO_GENERATE} sims.")


if __name__ == "__main__":
    generate_test_queue_file()
