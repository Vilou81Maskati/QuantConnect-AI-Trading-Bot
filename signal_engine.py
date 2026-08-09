from AlgorithmImports import *


class SignalEngine:

    def __init__(self, config):

        self.config = config

    # ==============================================================
    # CALCUL DU SCORE
    # ==============================================================

    def CalculateScore(self, features):

        if features is None:
            return 0

        price = float(features["price"])
        ema_fast = float(features["ema_fast"])
        ema_slow = float(features["ema_slow"])
        rsi = float(features["rsi"])
        atr = float(features["atr"])
        adx = float(features["adx"])
        macd = float(features["macd"])
        macd_signal = float(features["macd_signal"])
        roc = float(features["roc"])
        relative_volume = float(
            features["relative_volume"]
        )

        if price <= 0 or atr <= 0:
            return 0

        score = 0

        # ==========================================================
        # 1. TENDANCE EMA
        # ==========================================================

        if ema_fast > ema_slow:

            score += 25

        elif ema_fast > ema_slow * 0.995:

            score += 10

        # ==========================================================
        # 2. POSITION DU PRIX
        # ==========================================================

        if price > ema_fast:

            score += 15

        elif price > ema_slow:

            score += 7

        # ==========================================================
        # 3. RSI
        # ==========================================================

        if (
            rsi >= self.config.RSI_MIN
            and
            rsi <= self.config.RSI_MAX
        ):

            score += 15

        elif rsi > self.config.RSI_MIN - 5:

            score += 7

        # ==========================================================
        # 4. ADX
        # ==========================================================

        if adx >= self.config.ADX_MIN:

            score += 15

        elif adx >= self.config.ADX_MIN - 5:

            score += 7

        # ==========================================================
        # 5. MACD
        # ==========================================================

        if macd > macd_signal:

            score += 15

        # ==========================================================
        # 6. MOMENTUM
        # ==========================================================

        if roc > 0:

            score += 10

        # ==========================================================
        # 7. VOLUME
        # ==========================================================

        if (
            relative_volume
            >=
            self.config.MIN_RELATIVE_VOLUME
        ):

            score += 5

        # ==========================================================
        # LIMITATION
        # ==========================================================

        return min(
            100,
            max(
                0,
                int(score)
            )
        )

    # ==============================================================
    # SIGNAL D'ACHAT
    # ==============================================================

    def IsLongSignal(self, features):

        if features is None:
            return False

        score = self.CalculateScore(
            features
        )

        if score < self.config.MIN_ENTRY_SCORE:
            return False

        # ----------------------------------------------------------
        # FILTRE TENDANCE
        # ----------------------------------------------------------

        if (
            features["ema_fast"]
            <=
            features["ema_slow"]
        ):

            return False

        # ----------------------------------------------------------
        # FILTRE RSI
        # ----------------------------------------------------------

        if (
            features["rsi"]
            <
            self.config.RSI_MIN
        ):

            return False

        if (
            features["rsi"]
            >
            self.config.RSI_MAX
        ):

            return False

        # ----------------------------------------------------------
        # FILTRE ADX
        # ----------------------------------------------------------

        if (
            features["adx"]
            <
            self.config.ADX_MIN
        ):

            return False

        # ----------------------------------------------------------
        # FILTRE MACD
        # ----------------------------------------------------------

        if (
            features["macd"]
            <=
            features["macd_signal"]
        ):

            return False

        return True

    # ==============================================================
    # SIGNAL DE SORTIE
    # ==============================================================

    def IsExitSignal(self, features):

        if features is None:
            return False

        # ----------------------------------------------------------
        # RSI TRES FAIBLE
        # ----------------------------------------------------------

        if (
            features["rsi"]
            <=
            self.config.RSI_EXIT
        ):

            return True

        # ----------------------------------------------------------
        # PERTE DE TENDANCE
        # ----------------------------------------------------------

        if (
            features["price"]
            <
            features["ema_slow"]
        ):

            return True

        # ----------------------------------------------------------
        # MACD NEGATIF
        # ----------------------------------------------------------

        if (
            features["macd"]
            <
            features["macd_signal"]
        ):

            return True

        return False

    # ==============================================================
    # SIGNAL COMPLET
    # ==============================================================

    def GetSignal(self, features):

        if features is None:

            return {
                "signal": "NONE",
                "score": 0
            }

        score = self.CalculateScore(
            features
        )

        # ----------------------------------------------------------
        # ACHAT
        # ----------------------------------------------------------

        if self.IsLongSignal(features):

            return {
                "signal": "LONG",
                "score": score
            }

        # ----------------------------------------------------------
        # SORTIE
        # ----------------------------------------------------------

        if self.IsExitSignal(features):

            return {
                "signal": "EXIT",
                "score": score
            }

        # ----------------------------------------------------------
        # ATTENTE
        # ----------------------------------------------------------

        return {
            "signal": "HOLD",
            "score": score
        }

    # ==============================================================
    # VERIFICATION RAPIDE D'ACHAT
    # ==============================================================

    def ShouldEnter(self, features):

        return self.IsLongSignal(
            features
        )

    # ==============================================================
    # VERIFICATION RAPIDE DE SORTIE
    # ==============================================================

    def ShouldExit(self, features):

        return self.IsExitSignal(
            features
        )

    # ==============================================================
    # INFORMATIONS DU SIGNAL
    # ==============================================================

    def GetSignalDetails(self, features):

        if features is None:

            return {
                "signal": "NONE",
                "score": 0,
                "trend": False,
                "momentum": False,
                "volume": False
            }

        return {

            "signal":
                self.GetSignal(
                    features
                )["signal"],

            "score":
                self.CalculateScore(
                    features
                ),

            "trend":
                features["ema_fast"]
                >
                features["ema_slow"],

            "momentum":
                features["roc"] > 0,

            "volume":
                features["relative_volume"]
                >=
                self.config.MIN_RELATIVE_VOLUME
        }
