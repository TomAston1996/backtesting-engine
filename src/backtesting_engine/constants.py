"""
This module defines constants used in the backtesting engine and strategies.
"""

CLOSE_COLUMN = "Close"
SIGNAL_COLUMN = "Signal"
CASH_COLUMN = "Cash"  # cash available for trading
POSITION_COLUMN = "Position"  # how many shares of the asset are held
HOLDINGS_COLUMN = "Holdings"  # value of the asset held
TOTAL_VALUE_COLUMN = "Total_Value"  # total value of the portfolio including cash and holdings

BUY = "BUY"
SELL = "SELL"
HOLD = "HOLD"


# Queue Manager constants
SIM_GROUP = "sim_group"
OUTPUT_DIR_LOCATION = "output_dir_location"
AUTHOR = "author"
SIMS = "sims"
SIM_ID = "sim_id"
STRATEGY = "strategy"
DATA = "data"
SOURCE = "source"
TICKER = "ticker"
START_DATE = "start_date"
END_DATE = "end_date"
SIM_CONFIG = "sim_config"
INITIAL_CASH = "initial_cash"
SLIPPAGE = "slippage"
COMMISSION = "commission"
TYPE = "type"
FIELDS = "fields"
