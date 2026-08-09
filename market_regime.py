from AlgorithmImports import *


class MarketRegime:

    BULL = "BULL"
    NEUTRAL = "NEUTRAL"
    BEAR = "BEAR"

    def __init__(self, algorithm, config):

        self.algorithm = algorithm
        self.config = config

        # ==========================================================
        # INDICATEURS DU MARCHE DE REFERENCE
        # ==========================================================

        self.spy = algorithm.AddEquity(
            "SPY",
            Resolution.Hour
        ).Symbol

        self.ema_fast = algorithm.EMA(
            self.spy,
            config.REGIME_FAST_EMA,
            Resolution.Hour
        )

        self.ema_slow = algorithm.EMA(
            self.spy,
            config.REGIME_SLOW_EMA,
            Resolution.Hour
        )

        self.rsi = algorithm.RSI(
            self.spy,
            config.REGIME_RSI_PERIOD,
            MovingAverageType.Wilders,
            Resolution.Hour
        )

        self.adx = algorithm.ADX(
            self.spy,
            config.REGIME_ADX_PERIOD,
            Resolution.Hour
        )

    # ==============================================================
    # INDICATEURS PRETS
    # ==============================================================

    def IsReady(self):

        return (

            self.ema_fast.IsReady
            and

            self.ema_slow.IsReady
            and

            self.rsi.IsReady
            and

            self.adx.IsReady

        )

    # ==============================================================
    # REGIME
    # ==============================================================

    def GetRegime(self):

        if not self.IsReady():

            return self.NEUTRAL

        fast = float(
            self.ema_fast.Current.Value
        )

        slow = float(
            self.ema_slow.Current.Value
        )

        rsi = float(
            self.rsi.Current.Value
        )

        adx = float(
            self.adx.Current.Value
        )

        # ==========================================================
        # MARCHE HAUSSIER
        # ==========================================================

        if (

            fast > slow

            and

            rsi >= self.config.REGIME_BULL_RSI

            and

            adx >= self.config.REGIME_MIN_ADX

        ):

            return self.BULL

        # ==========================================================
        # MARCHE BAISSIER
        # ==========================================================

        if (

            fast < slow

            and

            rsi <= self.config.REGIME_BEAR_RSI

        ):

            return self.BEAR

        # ==========================================================
        # MARCHE NEUTRE
        # ==========================================================

        return self.NEUTRAL

    # ==============================================================
    # AUTORISATION DES ACHATS
    # ==============================================================

    def AllowLongEntries(self):

        regime = self.GetRegime()

        # ----------------------------------------------------------
        # MODE HAUSSIER
        # ----------------------------------------------------------

        if regime == self.BULL:

            return True

        # ----------------------------------------------------------
        # MODE NEUTRE
        # ----------------------------------------------------------

        if regime == self.NEUTRAL:

            return self.config.ALLOW_NEUTRAL_ENTRIES

        # ----------------------------------------------------------
        # MODE BAISSIER
        # ----------------------------------------------------------

        return False

    # ==============================================================
    # RAPPORT
    # ==============================================================

    def GetReport(self):

        return {

            "regime":
                self.GetRegime(),

            "allow_long":
                self.AllowLongEntries()

        }
