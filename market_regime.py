from AlgorithmImports import *


class MarketRegime:

    def __init__(
        self,
        algorithm,
        config
    ):

        self.algorithm = algorithm
        self.config = config

        # ==========================================================
        # ACTIF DE REFERENCE
        # ==========================================================

        self.symbol = None

        # ==========================================================
        # INDICATEURS
        # ==========================================================

        self.fast_ema = None
        self.slow_ema = None
        self.rsi = None
        self.adx = None

        # ==========================================================
        # INITIALISATION
        # ==========================================================

        self.InitializeIndicators()

    # ==============================================================
    # INITIALISATION
    # ==============================================================

    def InitializeIndicators(self):

        if not self.config.SYMBOLS:

            return

        # ----------------------------------------------------------
        # UTILISATION DE SPY COMME REFERENCE
        # ----------------------------------------------------------

        ticker = "SPY"

        if ticker not in self.config.SYMBOLS:

            ticker = self.config.SYMBOLS[0]

        security = self.algorithm.AddEquity(
            ticker,
            Resolution.Hour
        )

        security.SetDataNormalizationMode(
            DataNormalizationMode.Adjusted
        )

        self.symbol = security.Symbol

        # ----------------------------------------------------------
        # EMA RAPIDE
        # ----------------------------------------------------------

        self.fast_ema = self.algorithm.EMA(
            self.symbol,
            self.config.REGIME_FAST_EMA,
            Resolution.Hour
        )

        # ----------------------------------------------------------
        # EMA LENTE
        # ----------------------------------------------------------

        self.slow_ema = self.algorithm.EMA(
            self.symbol,
            self.config.REGIME_SLOW_EMA,
            Resolution.Hour
        )

        # ----------------------------------------------------------
        # RSI
        # ----------------------------------------------------------

        self.rsi = self.algorithm.RSI(
            self.symbol,
            self.config.REGIME_RSI_PERIOD,
            MovingAverageType.Wilders,
            Resolution.Hour
        )

        # ----------------------------------------------------------
        # ADX
        # ----------------------------------------------------------

        self.adx = self.algorithm.ADX(
            self.symbol,
            self.config.REGIME_ADX_PERIOD,
            Resolution.Hour
        )

    # ==============================================================
    # INDICATEURS PRETS
    # ==============================================================

    def IsReady(self):

        if self.fast_ema is None:
            return False

        if self.slow_ema is None:
            return False

        if self.rsi is None:
            return False

        if self.adx is None:
            return False

        return (
            self.fast_ema.IsReady
            and
            self.slow_ema.IsReady
            and
            self.rsi.IsReady
            and
            self.adx.IsReady
        )

    # ==============================================================
    # REGIME ACTUEL
    # ==============================================================

    def GetRegime(self):

        if not self.IsReady():

            return "UNKNOWN"

        # ----------------------------------------------------------
        # VALEURS
        # ----------------------------------------------------------

        fast = float(
            self.fast_ema.Current.Value
        )

        slow = float(
            self.slow_ema.Current.Value
        )

        rsi = float(
            self.rsi.Current.Value
        )

        adx = float(
            self.adx.Current.Value
        )

        # ----------------------------------------------------------
        # REGIME HAUSSIER
        # ----------------------------------------------------------

        if (
            fast > slow
            and
            rsi >= self.config.REGIME_BULL_RSI
            and
            adx >= self.config.REGIME_MIN_ADX
        ):

            return "BULL"

        # ----------------------------------------------------------
        # REGIME BAISSIER
        # ----------------------------------------------------------

        if (
            fast < slow
            and
            rsi < self.config.REGIME_BEAR_RSI
            and
            adx >= self.config.REGIME_MIN_ADX
        ):

            return "BEAR"

        # ----------------------------------------------------------
        # REGIME NEUTRE
        # ----------------------------------------------------------

        return "NEUTRAL"

    # ==============================================================
    # AUTORISATION DES ACHATS
    # ==============================================================

    def AllowLongEntries(self):

        regime = self.GetRegime()

        # ----------------------------------------------------------
        # MARCHE HAUSSIER
        # ----------------------------------------------------------

        if regime == "BULL":

            return True

        # ----------------------------------------------------------
        # MARCHE NEUTRE
        # ----------------------------------------------------------

        if regime == "NEUTRAL":

            return (
                self.config
                .ALLOW_NEUTRAL_ENTRIES
            )

        # ----------------------------------------------------------
        # MARCHE BAISSIER
        # ----------------------------------------------------------

        return False

    # ==============================================================
    # MARCHE BAISSIER
    # ==============================================================

    def IsBearMarket(self):

        return (
            self.GetRegime()
            ==
            "BEAR"
        )

    # ==============================================================
    # MARCHE HAUSSIER
    # ==============================================================

    def IsBullMarket(self):

        return (
            self.GetRegime()
            ==
            "BULL"
        )

    # ==============================================================
    # MARCHE NEUTRE
    # ==============================================================

    def IsNeutralMarket(self):

        return (
            self.GetRegime()
            ==
            "NEUTRAL"
        )

    # ==============================================================
    # RAPPORT
    # ==============================================================

    def GetReport(self):

        if not self.IsReady():

            return {

                "regime":
                    "UNKNOWN",

                "fast_ema":
                    None,

                "slow_ema":
                    None,

                "rsi":
                    None,

                "adx":
                    None

            }

        return {

            "regime":
                self.GetRegime(),

            "fast_ema":
                float(
                    self.fast_ema.Current.Value
                ),

            "slow_ema":
                float(
                    self.slow_ema.Current.Value
                ),

            "rsi":
                float(
                    self.rsi.Current.Value
                ),

            "adx":
                float(
                    self.adx.Current.Value
                )

        }
