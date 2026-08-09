"""
Moteur de génération des signaux.

Le moteur reçoit les caractéristiques calculées par indicators.py
et produit des signaux de recherche :

    BUY  = conditions favorables à une entrée
    HOLD = aucune action
    EXIT = conditions défavorables à une position existante

Les paramètres sont volontairement centralisés dans Config.
"""

from enum import Enum


class Signal(Enum):

    BUY = "BUY"
    HOLD = "HOLD"
    EXIT = "EXIT"


class SignalEngine:

    def __init__(self, config):

        self.config = config

    # ==============================================================
    # SCORE D'ENTREE
    # ==============================================================

    def CalculateEntryScore(self, features):

        if features is None:

            return 0

        score = 0

        # ----------------------------------------------------------
        # 1. TENDANCE PRINCIPALE
        # ----------------------------------------------------------

        if (
            features["ema_fast"]
            >
            features["ema_slow"]
        ):

            score += 25

        else:

            return 0

        # ----------------------------------------------------------
        # 2. POSITION DU PRIX
        # ----------------------------------------------------------

        if (
            features["price"]
            >
            features["ema_fast"]
        ):

            score += 15

        # ----------------------------------------------------------
        # 3. RSI
        # ----------------------------------------------------------

        if (
            self.config.RSI_MIN
            <=
            features["rsi"]
            <=
            self.config.RSI_MAX
        ):

            score += 20

        elif (
            features["rsi"]
            >=
            50
        ):

            score += 10

        # ----------------------------------------------------------
        # 4. MACD
        # ----------------------------------------------------------

        if (
            features["macd"]
            >
            features["macd_signal"]
        ):

            score += 15

        # ----------------------------------------------------------
        # 5. ADX
        # ----------------------------------------------------------

        if (
            features["adx"]
            >=
            self.config.ADX_MIN
        ):

            score += 15

        # ----------------------------------------------------------
        # 6. VOLUME
        # ----------------------------------------------------------

        if (
            features["relative_volume"]
            >=
            self.config.MIN_RELATIVE_VOLUME
        ):

            score += 5

        # ----------------------------------------------------------
        # 7. ROC
        # ----------------------------------------------------------

        if (
            features["roc"]
            >
            0
        ):

            score += 5

        return score

    # ==============================================================
    # VERIFICATION D'ENTREE
    # ==============================================================

    def CanEnter(self, features):

        if features is None:

            return False

        # Prix minimum
        if (
            features["price"]
            <
            self.config.MINIMUM_PRICE
        ):

            return False

        # Tendance haussière obligatoire
        if not (
            features["ema_fast"]
            >
            features["ema_slow"]
        ):

            return False

        # RSI trop élevé = éviter une entrée potentiellement
        # trop éloignée de sa zone normale de momentum
        if (
            features["rsi"]
            >
            self.config.RSI_MAX
        ):

            return False

        # Score global
        score = self.CalculateEntryScore(
            features
        )

        if (
            score
            <
            self.config.MIN_ENTRY_SCORE
        ):

            return False

        return True

    # ==============================================================
    # SIGNAL D'ENTREE
    # ==============================================================

    def GetEntrySignal(self, features):

        if self.CanEnter(features):

            return Signal.BUY

        return Signal.HOLD

    # ==============================================================
    # DETECTION DE SORTIE
    # ==============================================================

    def GetExitSignal(
        self,
        features,
        entry_price
    ):

        if features is None:

            return Signal.HOLD

        # ----------------------------------------------------------
        # TENDANCE
        # ----------------------------------------------------------

        if (
            features["ema_fast"]
            <
            features["ema_slow"]
        ):

            return Signal.EXIT

        # ----------------------------------------------------------
        # RSI
        # ----------------------------------------------------------

        if (
            features["rsi"]
            <
            self.config.RSI_EXIT
        ):

            return Signal.EXIT

        # ----------------------------------------------------------
        # MACD
        # ----------------------------------------------------------

        if (
            features["macd"]
            <
            features["macd_signal"]
        ):

            return Signal.EXIT

        # ----------------------------------------------------------
        # PROTECTION EXTREME
        # ----------------------------------------------------------

        if entry_price > 0:

            loss_ratio = (
                features["price"]
                /
                entry_price
            )

            if loss_ratio <= 0.50:

                return Signal.EXIT

        return Signal.HOLD

    # ==============================================================
    # ANALYSE COMPLETE
    # ==============================================================

    def Analyze(
        self,
        features,
        invested=False,
        entry_price=0
    ):

        if features is None:

            return {
                "signal": Signal.HOLD,
                "score": 0,
                "reasons": []
            }

        score = self.CalculateEntryScore(
            features
        )

        reasons = []

        # ----------------------------------------------------------
        # POSITION EXISTANTE
        # ----------------------------------------------------------

        if invested:

            signal = self.GetExitSignal(
                features,
                entry_price
            )

            if signal == Signal.EXIT:

                if (
                    features["ema_fast"]
                    <
                    features["ema_slow"]
                ):

                    reasons.append(
                        "TREND_REVERSAL"
                    )

                if (
                    features["rsi"]
                    <
                    self.config.RSI_EXIT
                ):

                    reasons.append(
                        "RSI_WEAKNESS"
                    )

                if (
                    features["macd"]
                    <
                    features["macd_signal"]
                ):

                    reasons.append(
                        "MACD_WEAKNESS"
                    )

                return {
                    "signal": Signal.EXIT,
                    "score": score,
                    "reasons": reasons
                }

            return {
                "signal": Signal.HOLD,
                "score": score,
                "reasons": []
            }

        # ----------------------------------------------------------
        # AUCUNE POSITION
        # ----------------------------------------------------------

        signal = self.GetEntrySignal(
            features
        )

        if signal == Signal.BUY:

            if (
                features["ema_fast"]
                >
                features["ema_slow"]
            ):

                reasons.append(
                    "UPTREND"
                )

            if (
                features["macd"]
                >
                features["macd_signal"]
            ):

                reasons.append(
                    "POSITIVE_MACD"
                )

            if (
                features["rsi"]
                >=
                self.config.RSI_MIN
            ):

                reasons.append(
                    "POSITIVE_MOMENTUM"
                )

            if (
                features["adx"]
                >=
                self.config.ADX_MIN
            ):

                reasons.append(
                    "TREND_STRENGTH"
                )

        return {
            "signal": signal,
            "score": score,
            "reasons": reasons
        }

    # ==============================================================
    # CLASSEMENT DES OPPORTUNITES
    # ==============================================================

    def RankCandidates(
        self,
        candidates
    ):

        """
        candidates doit contenir des dictionnaires
        ayant au minimum :

            {
                "symbol": symbol,
                "score": score,
                "features": features
            }

        Les meilleurs scores sont placés en premier.
        """

        return sorted(
            candidates,
            key=lambda x: x["score"],
            reverse=True
        )

    # ==============================================================
    # MEILLEURE OPPORTUNITE
    # ==============================================================

    def BestCandidate(
        self,
        candidates
    ):

        if not candidates:

            return None

        ranked = self.RankCandidates(
            candidates
        )

        return ranked[0]
