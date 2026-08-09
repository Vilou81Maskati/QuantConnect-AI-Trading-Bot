"""
Gestion du risque du portefeuille.

Le RiskManager détermine :
- le capital risqué par transaction ;
- la taille maximale d'une position ;
- le nombre maximal de positions ;
- les protections contre les pertes journalières ;
- la protection contre un drawdown important.

Les paramètres sont définis dans config.py.
"""

from AlgorithmImports import *


class RiskManager:

    def __init__(self, algorithm, config):

        self.algorithm = algorithm
        self.config = config

        # Valeur du portefeuille au début de la journée
        self.day_start_value = (
            float(
                algorithm.Portfolio.TotalPortfolioValue
            )
        )

        # Plus haut historique du portefeuille
        self.peak_value = (
            float(
                algorithm.Portfolio.TotalPortfolioValue
            )
        )

        # Etat du verrouillage
        self.locked = False

    # ==============================================================
    # MISE A JOUR DU PLUS HAUT DU PORTEFEUILLE
    # ==============================================================

    def UpdatePeak(self):

        current_value = (
            float(
                self.algorithm.Portfolio.TotalPortfolioValue
            )
        )

        if current_value > self.peak_value:

            self.peak_value = current_value

    # ==============================================================
    # NOUVELLE JOURNEE
    # ==============================================================

    def ResetDailyRisk(self):

        self.day_start_value = (
            float(
                self.algorithm.Portfolio.TotalPortfolioValue
            )
        )

        self.locked = False

    # ==============================================================
    # PERTE JOURNALIERE
    # ==============================================================

    def DailyLossPercent(self):

        if self.day_start_value <= 0:

            return 0.0

        current_value = (
            float(
                self.algorithm.Portfolio.TotalPortfolioValue
            )
        )

        loss = (
            self.day_start_value
            -
            current_value
        )

        return max(
            0.0,
            loss /
            self.day_start_value
        )

    # ==============================================================
    # DRAWDOWN
    # ==============================================================

    def DrawdownPercent(self):

        if self.peak_value <= 0:

            return 0.0

        current_value = (
            float(
                self.algorithm.Portfolio.TotalPortfolioValue
            )
        )

        drawdown = (
            self.peak_value
            -
            current_value
        )

        return max(
            0.0,
            drawdown /
            self.peak_value
        )

    # ==============================================================
    # VERIFICATION DU RISQUE
    # ==============================================================

    def CheckRiskLimits(self):

        daily_loss = (
            self.DailyLossPercent()
        )

        drawdown = (
            self.DrawdownPercent()
        )

        # ----------------------------------------------------------
        # LIMITE JOURNALIERE
        # ----------------------------------------------------------

        if (
            daily_loss
            >=
            self.config.MAX_DAILY_LOSS
        ):

            self.locked = True

            return False

        # ----------------------------------------------------------
        # DRAWDOWN MAXIMUM
        # ----------------------------------------------------------

        if (
            drawdown
            >=
            self.config.MAX_DRAWDOWN
        ):

            self.locked = True

            return False

        return True

    # ==============================================================
    # ETAT DU SYSTEME
    # ==============================================================

    def IsLocked(self):

        return self.locked

    # ==============================================================
    # CAPITAL A RISQUER
    # ==============================================================

    def RiskCapital(self):

        portfolio_value = (
            float(
                self.algorithm.Portfolio.TotalPortfolioValue
            )
        )

        return (
            portfolio_value
            *
            self.config.RISK_PER_TRADE
        )

    # ==============================================================
    # DISTANCE DU STOP
    # ==============================================================

    def StopDistance(self, atr):

        if atr <= 0:

            return 0.0

        return (
            atr
            *
            self.config.STOP_ATR_MULTIPLIER
        )

    # ==============================================================
    # QUANTITE SELON LE RISQUE
    # ==============================================================

    def QuantityFromRisk(
        self,
        price,
        atr
    ):

        if price <= 0:

            return 0

        if atr <= 0:

            return 0

        stop_distance = (
            self.StopDistance(
                atr
            )
        )

        if stop_distance <= 0:

            return 0

        risk_capital = (
            self.RiskCapital()
        )

        # ----------------------------------------------------------
        # FORMULE
        #
        # quantité =
        # capital risqué / distance du stop
        # ----------------------------------------------------------

        raw_quantity = (
            risk_capital
            /
            stop_distance
        )

        quantity = int(
            raw_quantity
        )

        return max(
            0,
            quantity
        )

    # ==============================================================
    # LIMITE DE VALEUR D'UNE POSITION
    # ==============================================================

    def MaxPositionQuantity(
        self,
        price
    ):

        if price <= 0:

            return 0

        portfolio_value = (
            float(
                self.algorithm.Portfolio.TotalPortfolioValue
            )
        )

        max_position_value = (
            portfolio_value
            *
            self.config.MAX_POSITION_ALLOCATION
        )

        quantity = int(
            max_position_value
            /
            price
        )

        return max(
            0,
            quantity
        )

    # ==============================================================
    # CAPITAL ENCORE DISPONIBLE
    # ==============================================================

    def AvailablePortfolioQuantity(
        self,
        price
    ):

        if price <= 0:

            return 0

        portfolio_value = (
            float(
                self.algorithm.Portfolio.TotalPortfolioValue
            )
        )

        invested_value = (
            float(
                self.algorithm.Portfolio.TotalHoldingsValue
            )
        )

        maximum_invested = (
            portfolio_value
            *
            self.config.MAX_TOTAL_ALLOCATION
        )

        available_value = (
            maximum_invested
            -
            invested_value
        )

        available_value = max(
            0.0,
            available_value
        )

        quantity = int(
            available_value
            /
            price
        )

        return max(
            0,
            quantity
        )

    # ==============================================================
    # QUANTITE FINALE
    # ==============================================================

    def CalculateQuantity(
        self,
        price,
        atr
    ):

        """
        Calcule la quantité finale en appliquant
        plusieurs limites simultanément.
        """

        if self.IsLocked():

            return 0

        # ----------------------------------------------------------
        # QUANTITE BASEE SUR LE RISQUE
        # ----------------------------------------------------------

        risk_quantity = (
            self.QuantityFromRisk(
                price,
                atr
            )
        )

        # ----------------------------------------------------------
        # LIMITE PAR POSITION
        # ----------------------------------------------------------

        position_limit = (
            self.MaxPositionQuantity(
                price
            )
        )

        # ----------------------------------------------------------
        # LIMITE PORTEFEUILLE
        # ----------------------------------------------------------

        portfolio_limit = (
            self.AvailablePortfolioQuantity(
                price
            )
        )

        # ----------------------------------------------------------
        # QUANTITE FINALE
        # ----------------------------------------------------------

        quantity = min(
            risk_quantity,
            position_limit,
            portfolio_limit
        )

        return max(
            0,
            quantity
        )

    # ==============================================================
    # NOMBRE DE POSITIONS
    # ==============================================================

    def InvestedPositions(
        self,
        symbols
    ):

        count = 0

        for symbol in symbols:

            if (
                self.algorithm
                .Portfolio[symbol]
                .Invested
            ):

                count += 1

        return count

    # ==============================================================
    # PLACES DISPONIBLES
    # ==============================================================

    def AvailableSlots(
        self,
        symbols
    ):

        current_positions = (
            self.InvestedPositions(
                symbols
            )
        )

        return max(
            0,
            self.config.MAX_POSITIONS
            -
            current_positions
        )

    # ==============================================================
    # RAPPORT RISQUE
    # ==============================================================

    def RiskReport(self):

        portfolio_value = (
            float(
                self.algorithm.Portfolio.TotalPortfolioValue
            )
        )

        return {

            "portfolio_value":
                portfolio_value,

            "risk_capital":
                self.RiskCapital(),

            "daily_loss":
                self.DailyLossPercent(),

            "drawdown":
                self.DrawdownPercent(),

            "locked":
                self.IsLocked()

        }
