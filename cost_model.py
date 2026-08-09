from AlgorithmImports import *


class RealisticCostModel:

    def __init__(self, algorithm, config):

        self.algorithm = algorithm
        self.config = config

    # ==============================================================
    # ESTIMATION DU COUT D'UNE TRANSACTION
    # ==============================================================

    def EstimateCost(
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
            *
            price
        )

        # ----------------------------------------------------------
        # COMMISSION
        # ----------------------------------------------------------

        commission = (
            notional
            *
            self.config.COMMISSION_RATE
        )

        # ----------------------------------------------------------
        # SLIPPAGE
        # ----------------------------------------------------------

        slippage = (
            notional
            *
            self.config.SLIPPAGE_RATE
        )

        # ----------------------------------------------------------
        # COUT TOTAL
        # ----------------------------------------------------------

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
                    1
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
                1
                -
                self.config.SLIPPAGE_RATE
            )
        )
