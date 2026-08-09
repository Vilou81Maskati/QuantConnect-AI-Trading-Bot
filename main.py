from AlgorithmImports import *

from config import Config
from indicators import IndicatorSet
from signal_engine import SignalEngine
from risk_manager import RiskManager
from trade_manager import TradeManager
from portfolio_manager import PortfolioManager
from statistics import StatisticsTracker


class QuantResearchStrategy(QCAlgorithm):

    def Initialize(self):

        # ==========================================================
        # CONFIGURATION
        # ==========================================================

        self.config = Config

        self.SetStartDate(2020, 1, 1)

        self.SetEndDate(2026, 8, 1)

        self.SetCash(
            self.config.INITIAL_CASH
        )

        # ==========================================================
        # INITIALISATION
        # ==========================================================

        self.symbols = []

        self.indicators = {}

        # ==========================================================
        # AJOUT DES ACTIFS
        # ==========================================================

        for ticker in self.config.SYMBOLS:

            security = self.AddEquity(
                ticker,
                Resolution.Hour
            )

            security.SetDataNormalizationMode(
                DataNormalizationMode.Adjusted
            )

            symbol = security.Symbol

            self.symbols.append(
                symbol
            )

            self.indicators[symbol] = (
                IndicatorSet(
                    self,
                    symbol,
                    self.config
                )
            )

        # ==========================================================
        # MODULES
        # ==========================================================

        self.signal_engine = (
            SignalEngine(
                self.config
            )
        )

        self.risk_manager = (
            RiskManager(
                self,
                self.config
            )
        )

        self.trade_manager = (
            TradeManager(
                self,
                self.config
            )
        )

        self.portfolio_manager = (
            PortfolioManager(
                self,
                self.config
            )
        )

        self.statistics = (
            StatisticsTracker(
                self
            )
        )

        # ==========================================================
        # WARMUP
        # ==========================================================

        self.SetWarmUp(
            self.config.WARMUP_DAYS,
            Resolution.Daily
        )

        # ==========================================================
        # HORLOGE
        # ==========================================================

        self.last_execution = None

        # ==========================================================
        # RESET QUOTIDIEN DU RISQUE
        # ==========================================================

        self.Schedule.On(

            self.DateRules.EveryDay(),

            self.TimeRules.At(
                9,
                35
            ),

            self.ResetDailyRisk
        )

        # ==========================================================
        # RAPPORT JOURNALIER
        # ==========================================================

        self.Schedule.On(

            self.DateRules.EveryDay(),

            self.TimeRules.At(
                15,
                55
            ),

            self.DailyReport
        )

    # ==============================================================
    # RESET RISQUE
    # ==============================================================

    def ResetDailyRisk(self):

        self.risk_manager.ResetDailyRisk()

    # ==============================================================
    # DONNEES MARCHE
    # ==============================================================

    def OnData(
        self,
        data
    ):

        # ----------------------------------------------------------
        # WARMUP
        # ----------------------------------------------------------

        if self.IsWarmingUp:

            return

        # ----------------------------------------------------------
        # MISE A JOUR DES PRIX
        # ----------------------------------------------------------

        for symbol in self.symbols:

            if symbol not in data.Bars:

                continue

            security = (
                self.Securities[
                    symbol
                ]
            )

            if not security.HasData:

                continue

            self.indicators[
                symbol
            ].UpdatePrice(
                security
            )

        # ----------------------------------------------------------
        # MISE A JOUR DU RISQUE
        # ----------------------------------------------------------

        self.risk_manager.UpdatePeak()

        # ----------------------------------------------------------
        # VERIFICATION RISQUE
        # ----------------------------------------------------------

        if not self.risk_manager.CheckRiskLimits():

            self.CloseAllPositions(
                "RISK_LIMIT"
            )

            return

        # ----------------------------------------------------------
        # GESTION DES POSITIONS
        # ----------------------------------------------------------

        self.ManageOpenPositions()

        # ----------------------------------------------------------
        # NOUVELLES POSITIONS
        # ----------------------------------------------------------

        self.LookForEntries()

        # ----------------------------------------------------------
        # STATISTIQUES
        # ----------------------------------------------------------

        self.statistics.UpdatePortfolioValue()

    # ==============================================================
    # GESTION DES POSITIONS EXISTANTES
    # ==============================================================

    def ManageOpenPositions(self):

        for symbol in self.symbols:

            # ------------------------------------------------------
            # PAS DE POSITION
            # ------------------------------------------------------

            if not self.Portfolio[
                symbol
            ].Invested:

                continue

            indicator = (
                self.indicators[
                    symbol
                ]
            )

            # ------------------------------------------------------
            # INDICATEURS NON PRETS
            # ------------------------------------------------------

            features = (
                indicator.GetFeatures()
            )

            if features is None:

                continue

            # ------------------------------------------------------
            # PRIX
            # ------------------------------------------------------

            price = (
                features[
                    "price"
                ]
            )

            atr = (
                features[
                    "atr"
                ]
            )

            # ------------------------------------------------------
            # MISE A JOUR TRADE
            # ------------------------------------------------------

            self.trade_manager.UpdateTrade(

                symbol,

                price,

                atr
            )

            # ------------------------------------------------------
            # VERIFICATION SORTIE
            # ------------------------------------------------------

            reason = (
                self.trade_manager.CheckExit(

                    symbol,

                    features,

                    self.signal_engine
                )
            )

            if reason is not None:

                self.ClosePosition(

                    symbol,

                    reason
                )

    # ==============================================================
    # RECHERCHE DE NOUVELLES ENTREES
    # ==============================================================

    def LookForEntries(self):

        # ----------------------------------------------------------
        # VERIFICATION DES PLACES
        # ----------------------------------------------------------

        available_slots = (
            self.portfolio_manager
            .GetAvailableSlots(
                self.symbols
            )
        )

        if available_slots <= 0:

            return

        # ----------------------------------------------------------
        # CONSTRUCTION DES CANDIDATS
        # ----------------------------------------------------------

        candidates = (
            self.portfolio_manager
            .BuildCandidates(

                self.symbols,

                self.indicators,

                self.signal_engine
            )
        )

        if not candidates:

            return

        # ----------------------------------------------------------
        # SELECTION
        # ----------------------------------------------------------

        selected = (
            self.portfolio_manager
            .SelectCandidates(

                candidates,

                available_slots
            )
        )

        # ----------------------------------------------------------
        # OUVERTURE
        # ----------------------------------------------------------

        for candidate in selected:

            self.OpenPosition(
                candidate
            )

    # ==============================================================
    # OUVERTURE POSITION
    # ==============================================================

    def OpenPosition(
        self,
        candidate
    ):

        symbol = (
            candidate[
                "symbol"
            ]
        )

        features = (
            candidate[
                "features"
            ]
        )

        score = (
            candidate[
                "score"
            ]
        )

        # ----------------------------------------------------------
        # PRIX
        # ----------------------------------------------------------

        price = (
            features[
                "price"
            ]
        )

        atr = (
            features[
                "atr"
            ]
        )

        # ----------------------------------------------------------
        # QUANTITE
        # ----------------------------------------------------------

        quantity = (
            self.risk_manager
            .CalculateQuantity(

                price,

                atr
            )
        )

        if quantity <= 0:

            return

        # ----------------------------------------------------------
        # VERIFICATION PORTEFEUILLE
        # ----------------------------------------------------------

        if not self.portfolio_manager.CanAddCapital(

            symbol,

            quantity
        ):

            return

        # ----------------------------------------------------------
        # TAG
        # ----------------------------------------------------------

        tag = (
            "BUY_SCORE_%d"
            %
            score
        )

        # ----------------------------------------------------------
        # ORDRE
        # ----------------------------------------------------------

        ticket = self.MarketOrder(

            symbol,

            quantity,

            tag=tag
        )

        if ticket is None:

            return

        # ----------------------------------------------------------
        # ENREGISTREMENT
        # ----------------------------------------------------------

        self.trade_manager.RegisterEntry(

            symbol,

            price,

            atr,

            score,

            tag
        )

        # ----------------------------------------------------------
        # LOG
        # ----------------------------------------------------------

        if self.config.DEBUG:

            self.Debug(

                "ENTRY | %s | "
                "Qty=%d | "
                "Price=%.2f | "
                "Score=%d"
                %
                (
                    symbol.Value,

                    quantity,

                    price,

                    score
                )
            )

    # ==============================================================
    # FERMETURE
    # ==============================================================

    def ClosePosition(
        self,
        symbol,
        reason
    ):

        if not self.Portfolio[
            symbol
        ].Invested:

            return

        # ----------------------------------------------------------
        # DONNEES POSITION
        # ----------------------------------------------------------

        quantity = (
            self.Portfolio[
                symbol
            ].Quantity
        )

        entry_price = float(
            self.Portfolio[
                symbol
            ].AveragePrice
        )

        current_price = float(
            self.Securities[
                symbol
            ].Price
        )

        # ----------------------------------------------------------
        # PNL
        # ----------------------------------------------------------

        pnl = (
            current_price
            -
            entry_price
        ) * quantity

        # ----------------------------------------------------------
        # INFORMATIONS TRADE
        # ----------------------------------------------------------

        trade = (
            self.trade_manager
            .GetTrade(
                symbol
            )
        )

        entry_time = (
            trade.entry_time
        )

        entry_score = (
            trade.entry_score
        )

        # ----------------------------------------------------------
        # LIQUIDATION
        # ----------------------------------------------------------

        self.Liquidate(

            symbol,

            tag="EXIT_" + reason
        )

        # ----------------------------------------------------------
        # STATISTIQUES
        # ----------------------------------------------------------

        self.statistics.RecordTrade(

            symbol,

            entry_price,

            current_price,

            quantity,

            entry_time,

            self.Time,

            entry_score,

            reason
        )

        # ----------------------------------------------------------
        # RESET
        # ----------------------------------------------------------

        self.trade_manager.CloseTrade(
            symbol
        )

        # ----------------------------------------------------------
        # LOG
        # ----------------------------------------------------------

        if self.config.DEBUG:

            self.Debug(

                "EXIT | %s | "
                "Reason=%s | "
                "PNL=%.2f"
                %
                (
                    symbol.Value,

                    reason,

                    pnl
                )
            )

    # ==============================================================
    # FERMETURE GENERALE
    # ==============================================================

    def CloseAllPositions(
        self,
        reason
    ):

        for symbol in self.symbols:

            if self.Portfolio[
                symbol
            ].Invested:

                self.ClosePosition(

                    symbol,

                    reason
                )

    # ==============================================================
    # RAPPORT
    # ==============================================================

    def DailyReport(self):

        if self.IsWarmingUp:

            return

        if not self.config.DEBUG:

            return

        self.portfolio_manager.PrintPortfolioReport()

    # ==============================================================
    # FIN DU BACKTEST
    # ==============================================================

    def OnEndOfAlgorithm(self):

        self.statistics.PrintReport()

        self.Debug(

            "FINAL VALUE = %.2f"
            %
            self.Portfolio
            .TotalPortfolioValue
        )
