from AlgorithmImports import *


class Config:

    # ==========================================================
    # CAPITAL INITIAL
    # ==========================================================

    INITIAL_CASH = 100000

    # ==========================================================
    # UNIVERS D'INVESTISSEMENT
    # ==========================================================

    SYMBOLS = [
        "SPY",
        "QQQ",
        "IWM",
        "DIA",
        "TLT"
    ]

    # ==========================================================
    # INDICATEURS PRINCIPAUX
    # ==========================================================

    EMA_FAST = 20
    EMA_SLOW = 50

    RSI_PERIOD = 14
    RSI_MIN = 45
    RSI_MAX = 70
    RSI_EXIT = 40

    ATR_PERIOD = 14

    ADX_PERIOD = 14
    ADX_MIN = 20

    MACD_FAST = 12
    MACD_SLOW = 26
    MACD_SIGNAL = 9

    ROC_PERIOD = 10

    VOLUME_PERIOD = 20
    MIN_RELATIVE_VOLUME = 0.80

    # ==========================================================
    # SCORE D'ENTREE
    # ==========================================================

    MIN_ENTRY_SCORE = 65

    # ==========================================================
    # RISQUE PAR POSITION
    # ==========================================================

    # 0,50 % du portefeuille par trade

    RISK_PER_TRADE = 0.005

    # ==========================================================
    # STOP LOSS
    # ==========================================================

    STOP_ATR_MULTIPLIER = 2.0

    # ==========================================================
    # TAKE PROFIT
    # ==========================================================

    TARGET_ATR_MULTIPLIER = 4.0

    # ==========================================================
    # TRAILING STOP
    # ==========================================================

    TRAILING_ATR_MULTIPLIER = 2.5

    # ==========================================================
    # ALLOCATION
    # ==========================================================

    MAX_POSITION_ALLOCATION = 0.35

    MAX_TOTAL_ALLOCATION = 0.90

    # ==========================================================
    # NOMBRE MAXIMUM DE POSITIONS
    # ==========================================================

    MAX_POSITIONS = 3

    # ==========================================================
    # PROTECTION DU CAPITAL
    # ==========================================================

    # Perte maximale journalière
    MAX_DAILY_LOSS = 0.02

    # Drawdown maximal du portefeuille
    MAX_DRAWDOWN = 0.15

    # ==========================================================
    # FILTRE DE PRIX
    # ==========================================================

    MINIMUM_PRICE = 10

    # ==========================================================
    # INITIALISATION DES INDICATEURS
    # ==========================================================

    WARMUP_DAYS = 60

    # ==========================================================
    # REGIME DE MARCHE
    # ==========================================================

    REGIME_FAST_EMA = 50

    REGIME_SLOW_EMA = 200

    REGIME_RSI_PERIOD = 14

    REGIME_ADX_PERIOD = 14

    REGIME_BULL_RSI = 50

    REGIME_BEAR_RSI = 45

    REGIME_MIN_ADX = 18

    # ----------------------------------------------------------
    # Si False :
    # le robot n'ouvre aucune nouvelle position en marché neutre.
    # ----------------------------------------------------------

    ALLOW_NEUTRAL_ENTRIES = False

    # ==========================================================
    # COUTS DE TRANSACTION
    # ==========================================================

    # Simulation de commission :
    # 0,05 %

    COMMISSION_RATE = 0.0005

    # Simulation de slippage :
    # 0,05 %

    SLIPPAGE_RATE = 0.0005

    # ==========================================================
    # SECURITE
    # ==========================================================

    # Taille maximale théorique d'une position
    MAX_POSITION_VALUE = 0.35

    # Pourcentage maximum du portefeuille exposé
    MAX_EXPOSURE = 0.90

    # ==========================================================
    # DEBUG
    # ==========================================================

    DEBUG = True
