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
SIM_GROUP = "simGroup"
OUTPUT_DIR_LOCATION = "outputDirLocation"
AUTHOR = "author"
SIMS = "sims"
SIM_ID = "simId"
STRATEGY = "strategy"
DATA = "data"
SOURCE = "source"
TICKER = "ticker"
START_DATE = "startDate"
END_DATE = "endDate"
SIM_CONFIG = "simConfig"
INITIAL_CASH = "initialCash"
SLIPPAGE = "slippage"
COMMISSION = "commission"
TYPE = "type"
FIELDS = "fields"
