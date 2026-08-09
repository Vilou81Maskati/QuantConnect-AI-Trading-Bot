from AlgorithmImports import *


class RiskManager:

    def __init__(self, algorithm, config):

        self.algorithm = algorithm
        self.config = config

        # ==========================================================
        # SUIVI DU CAPITAL
        # ==========================================================

        self.starting_value = (
            algorithm.Portfolio.TotalPortfolioValue
        )

        self.peak_value = (
            self.starting_value
        )

        self.day_start_value = (
            self.starting_value
        )

        self.trading_locked = False

        self.current_date = None

    # ==============================================================
    # RESET QUOTIDIEN
    # ==============================================================

    def ResetDailyRisk(self):

        self.day_start_value = (
            self.algorithm.Portfolio
            .TotalPortfolioValue
        )

        self.current_date = (
            self.algorithm.Time.date()
        )

        self.trading_locked = False

    # ==============================================================
    # MISE A JOUR DU PLUS HAUT CAPITAL
    # ==============================================================

    def UpdatePeak(self):

        current_value = (
            self.algorithm.Portfolio
            .TotalPortfolioValue
        )

        if current_value > self.peak_value:

            self.peak_value = current_value

    # ==============================================================
    # DRAWdown ACTUEL
    # ==============================================================

    def CurrentDrawdown(self):

        if self.peak_value <= 0:

            return 0.0

        current_value = (
            self.algorithm.Portfolio
            .TotalPortfolioValue
        )

        drawdown = (
            self.peak_value
            -
            current_value
        ) / self.peak_value

        return max(
            0.0,
            drawdown
        )

    # ==============================================================
    # PERTE QUOTIDIENNE
    # ==============================================================

    def CurrentDailyLoss(self):

        if self.day_start_value <= 0:

            return 0.0

        current_value = (
            self.algorithm.Portfolio
            .TotalPortfolioValue
        )

        loss = (
            self.day_start_value
            -
            current_value
        ) / self.day_start_value

        return max(
            0.0,
            loss
        )

    # ==============================================================
    # VERIFICATION DES LIMITES
    # ==============================================================

    def CheckRiskLimits(self):

        # ----------------------------------------------------------
        # SI DEJA BLOQUE
        # ----------------------------------------------------------

        if self.trading_locked:

            return False

        # ----------------------------------------------------------
        # MISE A JOUR
        # ----------------------------------------------------------

        self.UpdatePeak()

        # ----------------------------------------------------------
        # PERTE JOURNALIERE
        # ----------------------------------------------------------

        daily_loss = (
            self.CurrentDailyLoss()
        )

        if (
            daily_loss
            >=
            self.config.MAX_DAILY_LOSS
        ):

            self.trading_locked = True

            if self.config.DEBUG:

                self.algorithm.Debug(
                    "RISK LOCK | "
                    "DAILY LOSS = %.2f%%"
                    %
                    (
                        daily_loss * 100
                    )
                )

            return False

        # ----------------------------------------------------------
        # DRAWDOWN
        # ----------------------------------------------------------

        drawdown = (
            self.CurrentDrawdown()
        )

        if (
            drawdown
            >=
            self.config.MAX_DRAWDOWN
        ):

            self.trading_locked = True

            if self.config.DEBUG:

                self.algorithm.Debug(
                    "RISK LOCK | "
                    "DRAWDOWN = %.2f%%"
                    %
                    (
                        drawdown * 100
                    )
                )

            return False

        return True

    # ==============================================================
    # CAPITAL DISPONIBLE
    # ==============================================================

    def AvailableCapital(self):

        return max(
            0.0,
            float(
                self.algorithm.Portfolio
                .MarginRemaining
            )
        )

    # ==============================================================
    # RISQUE FINANCIER PAR TRADE
    # ==============================================================

    def RiskCapital(self):

        portfolio_value = float(
            self.algorithm.Portfolio
            .TotalPortfolioValue
        )

        return (
            portfolio_value
            *
            self.config.RISK_PER_TRADE
        )

    # ==============================================================
    # CALCUL DE LA QUANTITE
    # ==============================================================

    def CalculateQuantity(
        self,
        price,
        atr
    ):

        # ----------------------------------------------------------
        # VERIFICATIONS
        # ----------------------------------------------------------

        if price <= 0:

            return 0

        if atr <= 0:

            return 0

        if self.trading_locked:

            return 0

        # ----------------------------------------------------------
        # CAPITAL
        # ----------------------------------------------------------

        portfolio_value = float(
            self.algorithm.Portfolio
            .TotalPortfolioValue
        )

        if portfolio_value <= 0:

            return 0

        # ----------------------------------------------------------
        # RISQUE MAXIMAL
        # ----------------------------------------------------------

        risk_capital = (
            portfolio_value
            *
            self.config.RISK_PER_TRADE
        )

        # ----------------------------------------------------------
        # DISTANCE DU STOP
        # ----------------------------------------------------------

        stop_distance = (
            atr
            *
            self.config.STOP_ATR_MULTIPLIER
        )

        if stop_distance <= 0:

            return 0

        # ----------------------------------------------------------
        # QUANTITE BASEE SUR LE RISQUE
        # ----------------------------------------------------------

        quantity_by_risk = int(
            risk_capital
            /
            stop_distance
        )

        if quantity_by_risk <= 0:

            return 0

        # ----------------------------------------------------------
        # LIMITE DE POSITION
        # ----------------------------------------------------------

        maximum_position_value = (
            portfolio_value
            *
            self.config.MAX_POSITION_ALLOCATION
        )

        quantity_by_allocation = int(
            maximum_position_value
            /
            price
        )

        if quantity_by_allocation <= 0:

            return 0

        # ----------------------------------------------------------
        # CAPITAL DISPONIBLE
        # ----------------------------------------------------------

        available_capital = (
            self.AvailableCapital()
        )

        quantity_by_cash = int(
            available_capital
            /
            price
        )

        # ----------------------------------------------------------
        # QUANTITE FINALE
        # ----------------------------------------------------------

        quantity = min(

            quantity_by_risk,

            quantity_by_allocation,

            quantity_by_cash

        )

        return max(
            0,
            int(quantity)
        )

    # ==============================================================
    # RISQUE THEORIQUE D'UNE POSITION
    # ==============================================================

    def EstimatePositionRisk(
        self,
        quantity,
        atr
    ):

        if quantity <= 0:

            return 0.0

        if atr <= 0:

            return 0.0

        stop_distance = (
            atr
            *
            self.config.STOP_ATR_MULTIPLIER
        )

        return (
            abs(quantity)
            *
            stop_distance
        )

    # ==============================================================
    # POURCENTAGE DE RISQUE
    # ==============================================================

    def EstimateRiskPercent(
        self,
        quantity,
        atr
    ):

        portfolio_value = float(
            self.algorithm.Portfolio
            .TotalPortfolioValue
        )

        if portfolio_value <= 0:

            return 0.0

        risk = self.EstimatePositionRisk(
            quantity,
            atr
        )

        return (
            risk
            /
            portfolio_value
        )

    # ==============================================================
    # INFORMATIONS DE RISQUE
    # ==============================================================

    def GetRiskReport(self):

        portfolio_value = float(
            self.algorithm.Portfolio
            .TotalPortfolioValue
        )

        return {

            "portfolio_value":
                portfolio_value,

            "peak_value":
                self.peak_value,

            "daily_loss":
                self.CurrentDailyLoss(),

            "drawdown":
                self.CurrentDrawdown(),

            "locked":
                self.trading_locked,

            "risk_per_trade":
                self.config.RISK_PER_TRADE

        }
