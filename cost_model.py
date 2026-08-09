from AlgorithmImports import *


class RealisticCostModel:

    def __init__(self, algorithm, config):

        self.algorithm = algorithm
        self.config = config

    # ==============================================================
    # COMMISSION
    # ==============================================================

    def EstimateCommission(
        self,
        price,
        quantity
    ):

        if price <= 0:
            return 0.0

        if quantity == 0:
            return 0.0

        notional = (
            abs(quantity)
            * price
        )

        return (
            notional
            * self.config.COMMISSION_RATE
        )

    # ==============================================================
    # SLIPPAGE
    # ==============================================================

    def EstimateSlippage(
        self,
        price,
        quantity
    ):

        if price <= 0:
            return 0.0

        if quantity == 0:
            return 0.0

        notional = (
            abs(quantity)
            * price
        )

        return (
            notional
            * self.config.SLIPPAGE_RATE
        )

    # ==============================================================
    # COUT TOTAL
    # ==============================================================

    def EstimateCost(
        self,
        price,
        quantity
    ):

        commission = (
            self.EstimateCommission(
                price,
                quantity
            )
        )

        slippage = (
            self.EstimateSlippage(
                price,
                quantity
            )
        )

        return (
            commission
            +
            slippage
        )

    # ==============================================================
    # PRIX D'EXECUTION ESTIME
    # ==============================================================

    def EstimatedExecutionPrice(
        self,
        price,
        quantity
    ):

        if price <= 0:
            return price

        if quantity == 0:
            return price

        # ----------------------------------------------------------
        # ACHAT
        # ----------------------------------------------------------

        if quantity > 0:

            return (
                price
                *
                (
                    1.0
                    +
                    self.config.SLIPPAGE_RATE
                )
            )

        # ----------------------------------------------------------
        # VENTE
        # ----------------------------------------------------------

        return (
            price
            *
            (
                1.0
                -
                self.config.SLIPPAGE_RATE
            )
        )

    # ==============================================================
    # RAPPORT
    # ==============================================================

    def GetCostReport(
        self,
        price,
        quantity
    ):

        commission = (
            self.EstimateCommission(
                price,
                quantity
            )
        )

        slippage = (
            self.EstimateSlippage(
                price,
                quantity
            )
        )

        total = (
            commission
            +
            slippage
        )

        return {

            "commission":
                commission,

            "slippage":
                slippage,

            "total":
                total

        }
