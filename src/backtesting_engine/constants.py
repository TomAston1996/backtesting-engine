'''
This module defines constants used in the backtesting engine and strategies.
'''


CLOSE_COLUMN = "Close"
SIGNAL_COLUMN = "Signal"
CASH_COLUMN = "Cash" # cash available for trading
POSITION_COLUMN = "Position" # how many shares of the asset are held
HOLDINGS_COLUMN = "Holdings" # value of the asset held
TOTAL_VALUE_COLUMN = "Total_Value" # total value of the portfolio including cash and holdings

BUY = "BUY"
SELL = "SELL"
HOLD = "HOLD"