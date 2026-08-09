"""
Gestionnaire de portefeuille.

Responsabilités :
- compter les positions ouvertes ;
- déterminer le nombre de places disponibles ;
- classer les opportunités ;
- éviter les concentrations excessives ;
- sélectionner les meilleurs candidats ;
- vérifier la capacité du portefeuille.

Le PortfolioManager ne passe aucun ordre.
"""

from AlgorithmImports import *


class PortfolioManager:

    def __init__(self, algorithm, config):

        self.algorithm = algorithm
        self.config = config

    # ==============================================================
    # POSITIONS ACTUELLEMENT OUVERTES
    # ==============================================================

    def GetInvestedSymbols(self, symbols):

        invested = []

        for symbol in symbols:

            if self.algorithm.Portfolio[symbol].Invested:

                invested.append(symbol)

        return invested

    # ==============================================================
    # NOMBRE DE POSITIONS
    # ==============================================================

    def GetPositionCount(self, symbols):

        return len(
            self.GetInvestedSymbols(
                symbols
            )
        )

    # ==============================================================
    # PLACES DISPONIBLES
    # ==============================================================

    def GetAvailableSlots(self, symbols):

        current_positions = (
            self.GetPositionCount(
                symbols
            )
        )

        available = (
            self.config.MAX_POSITIONS
            -
            current_positions
        )

        return max(
            0,
            available
        )

    # ==============================================================
    # VALEUR DU PORTEFEUILLE
    # ==============================================================

    def PortfolioValue(self):

        return float(
            self.algorithm
            .Portfolio
            .TotalPortfolioValue
        )

    # ==============================================================
    # VALEUR INVESTIE
    # ==============================================================

    def InvestedValue(self):

        return float(
            self.algorithm
            .Portfolio
            .TotalHoldingsValue
        )

    # ==============================================================
    # POURCENTAGE INVESTI
    # ==============================================================

    def InvestedPercent(self):

        total = (
            self.PortfolioValue()
        )

        if total <= 0:

            return 0.0

        invested = (
            self.InvestedValue()
        )

        return (
            invested
            /
            total
        )

    # ==============================================================
    # CAPITAL DISPONIBLE
    # ==============================================================

    def AvailableCapital(self):

        total = (
            self.PortfolioValue()
        )

        maximum_invested = (
            total
            *
            self.config.MAX_TOTAL_ALLOCATION
        )

        invested = (
            self.InvestedValue()
        )

        return max(
            0.0,
            maximum_invested
            -
            invested
        )

    # ==============================================================
    # ALLOCATION D'UN ACTIF
    # ==============================================================

    def SymbolAllocation(
        self,
        symbol
    ):

        total = (
            self.PortfolioValue()
        )

        if total <= 0:

            return 0.0

        holding_value = abs(
            float(
                self.algorithm
                .Portfolio[symbol]
                .HoldingsValue
            )
        )

        return (
            holding_value
            /
            total
        )

    # ==============================================================
    # VERIFICATION DE CONCENTRATION
    # ==============================================================

    def CanAddCapital(
        self,
        symbol,
        quantity
    ):

        if quantity <= 0:

            return False

        price = float(
            self.algorithm
            .Securities[symbol]
            .Price
        )

        if price <= 0:

            return False

        position_value = (
            quantity
            *
            price
        )

        portfolio_value = (
            self.PortfolioValue()
        )

        if portfolio_value <= 0:

            return False

        maximum_position_value = (
            portfolio_value
            *
            self.config.MAX_POSITION_ALLOCATION
        )

        current_value = abs(
            float(
                self.algorithm
                .Portfolio[symbol]
                .HoldingsValue
            )
        )

        final_value = (
            current_value
            +
            position_value
        )

        if (
            final_value
            >
            maximum_position_value
        ):

            return False

        # ----------------------------------------------------------
        # VERIFICATION DU PORTEFEUILLE GLOBAL
        # ----------------------------------------------------------

        invested_after = (
            self.InvestedValue()
            +
            position_value
        )

        maximum_total = (
            portfolio_value
            *
            self.config.MAX_TOTAL_ALLOCATION
        )

        if (
            invested_after
            >
            maximum_total
        ):

            return False

        return True

    # ==============================================================
    # PREPARATION DES CANDIDATS
    # ==============================================================

    def BuildCandidates(
        self,
        symbols,
        indicators,
        signal_engine
    ):

        candidates = []

        for symbol in symbols:

            # ------------------------------------------------------
            # POSITION DEJA OUVERTE
            # ------------------------------------------------------

            if (
                self.algorithm
                .Portfolio[symbol]
                .Invested
            ):

                continue

            indicator = (
                indicators.get(
                    symbol
                )
            )

            if indicator is None:

                continue

            # ------------------------------------------------------
            # INDICATEURS
            # ------------------------------------------------------

            features = (
                indicator.GetFeatures()
            )

            if features is None:

                continue

            # ------------------------------------------------------
            # ANALYSE
            # ------------------------------------------------------

            analysis = (
                signal_engine.Analyze(
                    features,
                    invested=False
                )
            )

            # ------------------------------------------------------
            # UNIQUEMENT LES ACHATS
            # ------------------------------------------------------

            if analysis["signal"].value != "BUY":

                continue

            # ------------------------------------------------------
            # CREATION DU CANDIDAT
            # ------------------------------------------------------

            candidates.append({

                "symbol":
                    symbol,

                "score":
                    analysis["score"],

                "features":
                    features,

                "reasons":
                    analysis["reasons"]

            })

        return candidates

    # ==============================================================
    # CLASSEMENT
    # ==============================================================

    def RankCandidates(
        self,
        candidates
    ):

        return sorted(

            candidates,

            key=lambda candidate:
                candidate["score"],

            reverse=True
        )

    # ==============================================================
    # SELECTION
    # ==============================================================

    def SelectCandidates(
        self,
        candidates,
        slots=None
    ):

        if not candidates:

            return []

        # ----------------------------------------------------------
        # NOMBRE DE PLACES
        # ----------------------------------------------------------

        if slots is None:

            slots = (
                self.config.MAX_POSITIONS
            )

        if slots <= 0:

            return []

        # ----------------------------------------------------------
        # CLASSEMENT
        # ----------------------------------------------------------

        ranked = (
            self.RankCandidates(
                candidates
            )
        )

        # ----------------------------------------------------------
        # SELECTION
        # ----------------------------------------------------------

        selected = ranked[:slots]

        return selected

    # ==============================================================
    # MEILLEUR CANDIDAT
    # ==============================================================

    def BestCandidate(
        self,
        candidates
    ):

        selected = (
            self.SelectCandidates(
                candidates,
                1
            )
        )

        if not selected:

            return None

        return selected[0]

    # ==============================================================
    # VERIFICATION DU PORTEFEUILLE
    # ==============================================================

    def PortfolioHealth(self):

        value = (
            self.PortfolioValue()
        )

        invested = (
            self.InvestedValue()
        )

        allocation = 0.0

        if value > 0:

            allocation = (
                invested
                /
                value
            )

        return {

            "portfolio_value":
                value,

            "invested_value":
                invested,

            "cash_available":
                max(
                    0.0,
                    value - invested
                ),

            "allocation":
                allocation,

            "positions":
                self.GetPositionCount(
                    self.config.SYMBOLS
                ),

            "max_positions":
                self.config.MAX_POSITIONS
        }

    # ==============================================================
    # RAPPORT
    # ==============================================================

    def PrintPortfolioReport(self):

        health = (
            self.PortfolioHealth()
        )

        self.algorithm.Debug(

            "PORTFOLIO | "
            "Value=%.2f | "
            "Invested=%.2f | "
            "Allocation=%.2f%% | "
            "Positions=%d/%d"
            % (

                health["portfolio_value"],

                health["invested_value"],

                health["allocation"] * 100,

                health["positions"],

                health["max_positions"]
            )
        )
