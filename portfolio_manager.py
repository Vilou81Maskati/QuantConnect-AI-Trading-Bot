from AlgorithmImports import *


class PortfolioCandidate:

    def __init__(
        self,
        symbol,
        features,
        score
    ):

        self.symbol = symbol

        self.features = features

        self.score = int(score)


class PortfolioManager:

    def __init__(
        self,
        algorithm,
        config
    ):

        self.algorithm = algorithm

        self.config = config

    # ==============================================================
    # NOMBRE DE POSITIONS ACTUELLES
    # ==============================================================

    def GetInvestedSymbols(self):

        invested = []

        for symbol in self.algorithm.Securities.Keys:

            if self.algorithm.Portfolio[
                symbol
            ].Invested:

                invested.append(
                    symbol
                )

        return invested

    # ==============================================================
    # NOMBRE DE PLACES DISPONIBLES
    # ==============================================================

    def GetAvailableSlots(
        self,
        symbols
    ):

        current_positions = 0

        for symbol in symbols:

            if self.algorithm.Portfolio[
                symbol
            ].Invested:

                current_positions += 1

        return max(
            0,
            self.config.MAX_POSITIONS
            -
            current_positions
        )

    # ==============================================================
    # CAPITAL ACTUELLEMENT INVESTI
    # ==============================================================

    def GetInvestedCapital(self):

        total = 0.0

        for symbol in self.algorithm.Securities.Keys:

            holding = (
                self.algorithm.Portfolio[
                    symbol
                ]
            )

            if not holding.Invested:

                continue

            market_value = abs(
                float(
                    holding.HoldingsValue
                )
            )

            total += market_value

        return total

    # ==============================================================
    # EXPOSITION ACTUELLE
    # ==============================================================

    def GetCurrentExposure(self):

        portfolio_value = float(
            self.algorithm.Portfolio
            .TotalPortfolioValue
        )

        if portfolio_value <= 0:

            return 0.0

        invested_capital = (
            self.GetInvestedCapital()
        )

        return (
            invested_capital
            /
            portfolio_value
        )

    # ==============================================================
    # CAPITAL DISPONIBLE POUR DE NOUVELLES POSITIONS
    # ==============================================================

    def GetAvailableAllocation(self):

        portfolio_value = float(
            self.algorithm.Portfolio
            .TotalPortfolioValue
        )

        if portfolio_value <= 0:

            return 0.0

        maximum_exposure = (
            portfolio_value
            *
            self.config.MAX_TOTAL_ALLOCATION
        )

        invested_capital = (
            self.GetInvestedCapital()
        )

        return max(
            0.0,
            maximum_exposure
            -
            invested_capital
        )

    # ==============================================================
    # VERIFICATION CAPITAL
    # ==============================================================

    def CanAddCapital(
        self,
        symbol,
        quantity
    ):

        if quantity <= 0:

            return False

        if not self.algorithm.Securities[
            symbol
        ].HasData:

            return False

        price = float(
            self.algorithm.Securities[
                symbol
            ].Price
        )

        if price <= 0:

            return False

        # ----------------------------------------------------------
        # VALEUR DE LA NOUVELLE POSITION
        # ----------------------------------------------------------

        new_position_value = (
            abs(quantity)
            *
            price
        )

        # ----------------------------------------------------------
        # LIMITE D'UNE POSITION
        # ----------------------------------------------------------

        portfolio_value = float(
            self.algorithm.Portfolio
            .TotalPortfolioValue
        )

        if portfolio_value <= 0:

            return False

        maximum_position_value = (
            portfolio_value
            *
            self.config.MAX_POSITION_ALLOCATION
        )

        if (
            new_position_value
            >
            maximum_position_value
        ):

            return False

        # ----------------------------------------------------------
        # EXPOSITION GLOBALE
        # ----------------------------------------------------------

        available = (
            self.GetAvailableAllocation()
        )

        if new_position_value > available:

            return False

        return True

    # ==============================================================
    # CONSTRUCTION DES CANDIDATS
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

            if self.algorithm.Portfolio[
                symbol
            ].Invested:

                continue

            # ------------------------------------------------------
            # DONNEES
            # ------------------------------------------------------

            if symbol not in indicators:

                continue

            indicator = indicators[
                symbol
            ]

            features = (
                indicator.GetFeatures()
            )

            if features is None:

                continue

            # ------------------------------------------------------
            # PRIX MINIMUM
            # ------------------------------------------------------

            price = float(
                features["price"]
            )

            if (
                price
                <
                self.config.MINIMUM_PRICE
            ):

                continue

            # ------------------------------------------------------
            # SIGNAL
            # ------------------------------------------------------

            if not signal_engine.ShouldEnter(
                features
            ):

                continue

            # ------------------------------------------------------
            # SCORE
            # ------------------------------------------------------

            score = (
                signal_engine.CalculateScore(
                    features
                )
            )

            if (
                score
                <
                self.config.MIN_ENTRY_SCORE
            ):

                continue

            candidates.append(
                PortfolioCandidate(
                    symbol,
                    features,
                    score
                )
            )

        return candidates

    # ==============================================================
    # SELECTION DES MEILLEURS CANDIDATS
    # ==============================================================

    def SelectCandidates(
        self,
        candidates,
        available_slots
    ):

        if not candidates:

            return []

        if available_slots <= 0:

            return []

        # ----------------------------------------------------------
        # TRI PAR SCORE
        # ----------------------------------------------------------

        sorted_candidates = sorted(

            candidates,

            key=lambda candidate:
                candidate.score,

            reverse=True

        )

        # ----------------------------------------------------------
        # LIMITATION
        # ----------------------------------------------------------

        selected = (
            sorted_candidates[
                :available_slots
            ]
        )

        return selected

    # ==============================================================
    # RAPPORT PORTEFEUILLE
    # ==============================================================

    def GetPortfolioReport(self):

        portfolio_value = float(
            self.algorithm.Portfolio
            .TotalPortfolioValue
        )

        invested_capital = (
            self.GetInvestedCapital()
        )

        exposure = (
            self.GetCurrentExposure()
        )

        positions = []

        for symbol in self.algorithm.Securities.Keys:

            holding = (
                self.algorithm.Portfolio[
                    symbol
                ]
            )

            if not holding.Invested:

                continue

            positions.append({

                "symbol":
                    symbol.Value,

                "quantity":
                    holding.Quantity,

                "average_price":
                    float(
                        holding.AveragePrice
                    ),

                "market_price":
                    float(
                        self.algorithm
                        .Securities[
                            symbol
                        ].Price
                    ),

                "unrealized_pnl":
                    float(
                        holding.UnrealizedProfit
                    )

            })

        return {

            "portfolio_value":
                portfolio_value,

            "invested_capital":
                invested_capital,

            "exposure":
                exposure,

            "positions":
                positions

        }

    # ==============================================================
    # AFFICHAGE DU RAPPORT
    # ==============================================================

    def PrintPortfolioReport(self):

        if not self.config.DEBUG:

            return

        report = (
            self.GetPortfolioReport()
        )

        self.algorithm.Debug(

            "PORTFOLIO | "
            "Value=%.2f | "
            "Invested=%.2f | "
            "Exposure=%.2f%%"
            %
            (
                report["portfolio_value"],

                report["invested_capital"],

                report["exposure"] * 100
            )
        )

        for position in report[
            "positions"
        ]:

            self.algorithm.Debug(

                "POSITION | "
                "%s | "
                "Qty=%s | "
                "Entry=%.2f | "
                "Price=%.2f | "
                "PnL=%.2f"
                %
                (
                    position["symbol"],

                    position["quantity"],

                    position["average_price"],

                    position["market_price"],

                    position["unrealized_pnl"]
                )
            )
