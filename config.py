"""
Configuration générale du robot
"""

# ==============================
# CAPITAL
# ==============================

STARTING_CASH = 100000

# ==============================
# UNIVERS
# ==============================

SYMBOLS = [

    "SPY",
    "QQQ",
    "DIA",
    "IWM",
    "TLT"

]

# ==============================
# INDICATEURS
# ==============================

EMA_FAST = 50
EMA_SLOW = 200

RSI_PERIOD = 14

MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

ADX_PERIOD = 14

ATR_PERIOD = 14

VOLUME_PERIOD = 20

VWAP_PERIOD = 20

# ==============================
# FILTRES
# ==============================

RSI_BUY = 55
RSI_SELL = 45

ADX_MIN = 25

# ==============================
# GESTION DU RISQUE
# ==============================

RISK_PER_TRADE = 0.01

MAX_POSITIONS = 2

MAX_PORTFOLIO_RISK = 0.10

# ATR

STOP_ATR = 2.0

TARGET_ATR = 4.0

TRAILING_ATR = 2.5

# ==============================
# REBALANCING
# ==============================

REBALANCE_DAYS = 5

# ==============================
# FILTRE DE MARCHE
# ==============================

MARKET_FILTER = "SPY"

MARKET_EMA = 200

# ==============================
# JOURNAL
# ==============================

DEBUG = True
