from AlgorithmImports import *


class IndicatorSet:

    def __init__(self, algorithm, symbol, config):

        self.algorithm = algorithm
        self.symbol = symbol
        self.config = config

        # ==========================================================
        # INDICATEURS
        # ==========================================================

        self.ema_fast = algorithm.EMA(
            symbol,
            config.EMA_FAST,
            Resolution.Hour
        )

        self.ema_slow = algorithm.EMA(
            symbol,
            config.EMA_SLOW,
            Resolution.Hour
        )

        self.rsi = algorithm.RSI(
            symbol,
            config.RSI_PERIOD,
            MovingAverageType.Wilders,
            Resolution.Hour
        )

        self.atr = algorithm.ATR(
            symbol,
            config.ATR_PERIOD,
            MovingAverageType.Wilders,
            Resolution.Hour
        )

        self.adx = algorithm.ADX(
            symbol,
            config.ADX_PERIOD,
            Resolution.Hour
        )

        self.macd = algorithm.MACD(
            symbol,
            config.MACD_FAST,
            config.MACD_SLOW,
            config.MACD_SIGNAL,
            MovingAverageType.Exponential,
            Resolution.Hour
        )

        self.roc = algorithm.ROC(
            symbol,
            config.ROC_PERIOD,
            Resolution.Hour
        )

        # ==========================================================
        # ETAT
        # ==========================================================

        self.last_price = 0.0
        self.last_volume = 0.0

        self.volume_window = []

        # ==========================================================
        # PREPARATION HISTORIQUE
        # ==========================================================

        self.ready = False

    # ==============================================================
    # MISE A JOUR DU PRIX / VOLUME
    # ==============================================================

    def UpdatePrice(self, security):

        if security is None:
            return

        if not security.HasData:
            return

        price = float(security.Price)

        if price <= 0:
            return

        self.last_price = price

        # ----------------------------------------------------------
        # VOLUME
        # ----------------------------------------------------------

        volume = float(
            security.Volume
        )

        if volume > 0:

            self.last_volume = volume

            self.volume_window.append(
                volume
            )

            if len(self.volume_window) > self.config.VOLUME_PERIOD:

                self.volume_window.pop(0)

        # ----------------------------------------------------------
        # VERIFICATION
        # ----------------------------------------------------------

        self.ready = self.IsReady()

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

            self.atr.IsReady
            and

            self.adx.IsReady
            and

            self.macd.IsReady
            and

            self.roc.IsReady

        )

    # ==============================================================
    # VOLUME MOYEN
    # ==============================================================

    def AverageVolume(self):

        if not self.volume_window:

            return 0.0

        return (
            sum(self.volume_window)
            /
            len(self.volume_window)
        )

    # ==============================================================
    # VOLUME RELATIF
    # ==============================================================

    def RelativeVolume(self):

        average = self.AverageVolume()

        if average <= 0:

            return 0.0

        if self.last_volume <= 0:

            return 0.0

        return (
            self.last_volume
            /
            average
        )

    # ==============================================================
    # FEATURES
    # ==============================================================

    def GetFeatures(self):

        if not self.IsReady():

            return None

        if self.last_price <= 0:

            return None

        return {

            "price":
                self.last_price,

            "ema_fast":
                float(
                    self.ema_fast.Current.Value
                ),

            "ema_slow":
                float(
                    self.ema_slow.Current.Value
                ),

            "rsi":
                float(
                    self.rsi.Current.Value
                ),

            "atr":
                float(
                    self.atr.Current.Value
                ),

            "adx":
                float(
                    self.adx.Current.Value
                ),

            "macd":
                float(
                    self.macd.Current.Value
                ),

            "macd_signal":
                float(
                    self.macd.Signal.Current.Value
                ),

            "roc":
                float(
                    self.roc.Current.Value
                ),

            "relative_volume":
                self.RelativeVolume()
        }

    # ==============================================================
    # DEBUG
    # ==============================================================

    def DebugFeatures(self):

        features = self.GetFeatures()

        if features is None:

            return

        self.algorithm.Debug(

            "INDICATORS | %s | "
            "Price %.2f | "
            "EMA %.2f/%.2f | "
            "RSI %.2f | "
            "ATR %.2f | "
            "ADX %.2f | "
            "MACD %.4f/%.4f"
            %
            (

                self.symbol.Value,

                features["price"],

                features["ema_fast"],

                features["ema_slow"],

                features["rsi"],

                features["atr"],

                features["adx"],

                features["macd"],

                features["macd_signal"]

            )
        )
