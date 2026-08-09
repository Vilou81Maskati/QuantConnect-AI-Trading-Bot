class Config:

    # =========================
    # PORTEFEUILLE
    # =========================

    INITIAL_CASH = 100000

    # =========================
    # UNIVERS
    # =========================

    SYMBOLS = [
        "SPY",
        "QQQ",
        "DIA",
        "IWM",
        "TLT"
    ]

    # =========================
    # TIMEFRAME
    # =========================

    RESOLUTION = "Hour"

    # =========================
    # INDICATEURS
    # =========================

    EMA_FAST = 50
    EMA_SLOW = 200

    RSI_PERIOD = 14

    MACD_FAST = 12
    MACD_SLOW = 26
    MACD_SIGNAL = 9

    ADX_PERIOD = 14

    ATR_PERIOD = 14

    BB_PERIOD = 20
    BB_STD = 2

    ROC_PERIOD = 20

    STOCH_PERIOD = 14
    STOCH_K = 3
    STOCH_D = 3

    VOLUME_PERIOD = 20

    # =========================
    # CONDITIONS D'ENTREE
    # =========================

    RSI_MIN = 55
    RSI_MAX = 70

    ADX_MIN = 20

    MIN_RELATIVE_VOLUME = 0.8

    # Score minimum pour autoriser
    # une entrée

    MIN_ENTRY_SCORE = 70

    # =========================
    # GESTION DU RISQUE
    # =========================

    RISK_PER_TRADE = 0.005

    MAX_POSITIONS = 2

    MAX_POSITION_ALLOCATION = 0.35

    MAX_TOTAL_ALLOCATION = 0.90

    # =========================
    # STOPS
    # =========================

    STOP_ATR_MULTIPLIER = 2.0

    TARGET_ATR_MULTIPLIER = 4.0

    TRAILING_ATR_MULTIPLIER = 2.5

    # =========================
    # PROTECTION DU PORTEFEUILLE
    # =========================

    MAX_DAILY_LOSS = 0.02

    MAX_DRAWDOWN = 0.15

    # =========================
    # DONNEES
    # =========================

    WARMUP_DAYS = 260

    MINIMUM_PRICE = 10

    # =========================
    # DEBUG
    # =========================

    DEBUG = True
