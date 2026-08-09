from AlgorithmImports import *


class IndicatorSet:

    def __init__(self, algorithm, symbol, config):

        self.algorithm = algorithm
        self.symbol = symbol
        self.config = config

        # ==========================================================
        # TENDANCE
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

        # ==========================================================
        # MOMENTUM
        # ==========================================================

        self.rsi = algorithm.RSI(
            symbol,
            config.RSI_PERIOD,
            MovingAverageType.Wilders,
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

        self.stochastic = algorithm.STO(
            symbol,
            config.STOCH_PERIOD,
            config.STOCH_K,
            config.STOCH_D,
            Resolution.Hour
        )

        # ==========================================================
        # FORCE DE TENDANCE
        # ==========================================================

        self.adx = algorithm.ADX(
            symbol,
            config.ADX_PERIOD,
            Resolution.Hour
        )

        # ==========================================================
        # VOLATILITE
        # ==========================================================

        self.atr = algorithm.ATR(
            symbol,
            config.ATR_PERIOD,
            MovingAverageType.Wilders,
            Resolution.Hour
        )

        self.bollinger = algorithm.BB(
            symbol,
            config.BB_PERIOD,
            config.BB_STD,
            MovingAverageType.Simple,
            Resolution.Hour
        )

        # ==========================================================
        # VOLUME
        # ==========================================================

        self.volume_sma = algorithm.SMA(
            symbol,
            config.VOLUME_PERIOD,
            Resolution.Hour,
            Field.Volume
        )

        # ==========================================================
        # DONNEES COURANTES
        # ==========================================================

        self.price = 0.0
        self.volume = 0.0

    # ==============================================================
    # VERIFICATION
    # ==============================================================

    def IsReady(self):

        return (

            self.ema_fast.IsReady
            and self.ema_slow.IsReady
            and self.rsi.IsReady
            and self.macd.IsReady
            and self.roc.IsReady
            and self.stochastic.IsReady
            and self.adx.IsReady
            and self.atr.IsReady
            and self.bollinger.IsReady
            and self.volume_sma.IsReady

        )

    # ==============================================================
    # MISE A JOUR DU PRIX
    # ==============================================================

    def UpdatePrice(self, security):

        self.price = float(security.Price)
        self.volume = float(security.Volume)

    # ==============================================================
    # RECUPERATION DES DONNEES
    # ==============================================================

    def GetFeatures(self):

        if not self.IsReady():

            return None

        if self.price <= 0:

            return None

        atr = float(
            self.atr.Current.Value
        )

        average_volume = float(
            self.volume_sma.Current.Value
        )

        relative_volume = 0

        if average_volume > 0:

            relative_volume = (
                self.volume /
                average_volume
            )

        # ----------------------------------------------------------
        # DONNEES
        # ----------------------------------------------------------

        features = {

            "price":
                self.price,

            # Tendance
            "ema_fast":
                float(
                    self.ema_fast.Current.Value
                ),

            "ema_slow":
                float(
                    self.ema_slow.Current.Value
                ),

            # RSI
            "rsi":
                float(
                    self.rsi.Current.Value
                ),

            # MACD
            "macd":
                float(
                    self.macd.Current.Value
                ),

            "macd_signal":
                float(
                    self.macd.Signal.Current.Value
                ),

            "macd_histogram":
                float(
                    self.macd.Histogram.Current.Value
                ),

            # ADX
            "adx":
                float(
                    self.adx.Current.Value
                ),

            # ATR
            "atr":
                atr,

            "atr_percent":
                atr / self.price,

            # Bollinger
            "bb_upper":
                float(
                    self.bollinger.UpperBand.Current.Value
                ),

            "bb_middle":
                float(
                    self.bollinger.MiddleBand.Current.Value
                ),

            "bb_lower":
                float(
                    self.bollinger.LowerBand.Current.Value
                ),

            # ROC
            "roc":
                float(
                    self.roc.Current.Value
                ),

            # Stochastic
            "stoch_k":
                float(
                    self.stochastic.StochK.Current.Value
                ),

            "stoch_d":
                float(
                    self.stochastic.StochD.Current.Value
                ),

            # Volume
            "volume":
                self.volume,

            "average_volume":
                average_volume,

            "relative_volume":
                relative_volume
        }

        return features

    # ==============================================================
    # SCORE DE TENDANCE
    # ==============================================================

    def TrendScore(self, features):

        score = 0

        # EMA rapide au-dessus de l'EMA lente
        if (
            features["ema_fast"]
            >
            features["ema_slow"]
        ):

            score += 25

        # Prix au-dessus de l'EMA rapide
        if (
            features["price"]
            >
            features["ema_fast"]
        ):

            score += 15

        # ADX
        if features["adx"] >= 25:

            score += 15

        elif features["adx"] >= 20:

            score += 10

        return score

    # ==============================================================
    # SCORE MOMENTUM
    # ==============================================================

    def MomentumScore(self, features):

        score = 0

        # RSI
        if (
            self.config.RSI_MIN
            <=
            features["rsi"]
            <=
            self.config.RSI_MAX
        ):

            score += 20

        elif features["rsi"] >= 50:

            score += 10

        # MACD
        if (
            features["macd"]
            >
            features["macd_signal"]
        ):

            score += 15

        # ROC positif
        if features["roc"] > 0:

            score += 10

        # Stochastic
        if (
            features["stoch_k"]
            >
            features["stoch_d"]
        ):

            score += 5

        return score

    # ==============================================================
    # SCORE VOLATILITE
    # ==============================================================

    def VolatilityScore(self, features):

        score = 0

        atr_percent = (
            features["atr_percent"]
        )

        # Volatilité suffisante
        if atr_percent > 0.005:

            score += 5

        # Mais pas excessivement élevée
        if atr_percent < 0.06:

            score += 5

        # Prix au-dessus de la moyenne Bollinger
        if (
            features["price"]
            >
            features["bb_middle"]
        ):

            score += 5

        return score

    # ==============================================================
    # SCORE VOLUME
    # ==============================================================

    def VolumeScore(self, features):

        relative_volume = (
            features["relative_volume"]
        )

        if relative_volume >= 1.5:

            return 10

        if relative_volume >= 1.0:

            return 7

        if (
            relative_volume
            >=
            self.config.MIN_RELATIVE_VOLUME
        ):

            return 5

        return 0

    # ==============================================================
    # SCORE GLOBAL
    # ==============================================================

    def TotalScore(self, features):

        if features is None:

            return 0

        trend = self.TrendScore(
            features
        )

        momentum = self.MomentumScore(
            features
        )

        volatility = self.VolatilityScore(
            features
        )

        volume = self.VolumeScore(
            features
        )

        total = (
            trend
            +
            momentum
            +
            volatility
            +
            volume
        )

        return total
