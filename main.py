from AlgorithmImports import *

from config import Config
from indicators import IndicatorSet
from signal_engine import SignalEngine
from risk_manager import RiskManager
from trade_manager import TradeManager
from portfolio_manager import PortfolioManager
from statistics import StatisticsTracker
from market_regime import MarketRegime


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
        # VARIABLES PRINCIPALES
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

            self.indicators[symbol] = IndicatorSet(
                self,
                symbol,
                self.config
            )

        # ==========================================================
        # MODULE DE SIGNAL
        # ==========================================================

        self.signal_engine = SignalEngine(
            self.config
        )

        # ==========================================================
        # GESTION DU RISQUE
        # ==========================================================

        self.risk_manager = RiskManager(
            self,
            self.config
        )

        # ==========================================================
        # GESTION DES TRADES
        # ==========================================================

        self.trade_manager = TradeManager(
            self,
            self.config
        )

        # ==========================================================
        # GESTION DU PORTEFEUILLE
        # ==========================================================

        self.portfolio_manager = PortfolioManager(
            self,
            self.config
        )

        # ==========================================================
        # STATISTIQUES
        # ==========================================================

        self.statistics = StatisticsTracker(
            self
        )

        # ==========================================================
        # REGIME DE MARCHE
        # ==========================================================

        self.market_regime = MarketRegime(
            self,
            self.config
        )

        # ==========================================================
        # WARMUP
        # ==========================================================

        self.SetWarmUp(
            self.config.WARMUP_DAYS,
            Resolution.Hour
        )

        # ==========================================================
        # HORLOGE
        # ==========================================================

        self.last_execution = None

        # ==========================================================
        # RESET RISQUE QUOTIDIEN
        # ==========================================================

        self.Schedule.On(
            self.DateRules.EveryDay(),
            self.TimeRules.At(9, 35),
            self.ResetDailyRisk
        )

        # ==========================================================
        # RAPPORT QUOTIDIEN
        # ==========================================================

        self.Schedule.On(
            self.DateRules.EveryDay(),
            self.TimeRules.At(15, 55),
            self.DailyReport
        )

    # ==============================================================
    # RESET DU RISQUE
    # ==============================================================

    def ResetDailyRisk(self):

        self.risk_manager.ResetDailyRisk()

    # ==============================================================
    # RECEPTION DES DONNEES
    # ==============================================================

    def OnData(self, data):

        # ----------------------------------------------------------
        # WARMUP
        # ----------------------------------------------------------

        if self.IsWarmingUp:

            return

        # ----------------------------------------------------------
        # MISE A JOUR DES INDICATEURS
        # ----------------------------------------------------------

        for symbol in self.symbols:

            if not data.Bars.ContainsKey(symbol):

                continue

            security = self.Securities[symbol]

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
        # VERIFICATION DES LIMITES
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
        # RECHERCHE DE NOUVELLES ENTREES
        # ----------------------------------------------------------

        self.LookForEntries()

        # ----------------------------------------------------------
        # STATISTIQUES
        # ----------------------------------------------------------

        self.statistics.UpdatePortfolioValue()

    # ==============================================================
    # GESTION DES POSITIONS OUVERTES
    # ==============================================================

    def ManageOpenPositions(self):

        for symbol in self.symbols:

            # ------------------------------------------------------
            # POSITION INACTIVE
            # ------------------------------------------------------

            if not self.Portfolio[
                symbol
            ].Invested:

                continue

            # ------------------------------------------------------
            # INDICATEURS
            # ------------------------------------------------------

            indicator = self.indicators[
                symbol
            ]

            features = indicator.GetFeatures()

            if features is None:

                continue

            # ------------------------------------------------------
            # PRIX
            # ------------------------------------------------------

            price = float(
                features["price"]
            )

            # ------------------------------------------------------
            # ATR
            # ------------------------------------------------------

            atr = float(
                features["atr"]
            )

            if price <= 0 or atr <= 0:

                continue

            # ------------------------------------------------------
            # MISE A JOUR DU TRADE
            # ------------------------------------------------------

            self.trade_manager.UpdateTrade(
                symbol,
                price,
                atr
            )

            # ------------------------------------------------------
            # VERIFICATION SORTIE
            # ------------------------------------------------------

            reason = self.trade_manager.CheckExit(
                symbol,
                features,
                self.signal_engine
            )

            if reason is not None:

                self.ClosePosition(
                    symbol,
                    reason
                )

    # ==============================================================
    # RECHERCHE DE NOUVELLES POSITIONS
    # ==============================================================

    def LookForEntries(self):

        # ----------------------------------------------------------
        # FILTRE DE REGIME
        # ----------------------------------------------------------

        if not self.market_regime.AllowLongEntries():

            return

        # ----------------------------------------------------------
        # PLACES DISPONIBLES
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
        # CREATION DES CANDIDATS
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
        # CLASSEMENT
        # ----------------------------------------------------------

        selected = (
            self.portfolio_manager
            .SelectCandidates(
                candidates,
                available_slots
            )
        )

        if not selected:

            return

        # ----------------------------------------------------------
        # OUVERTURE DES POSITIONS
        # ----------------------------------------------------------

        for candidate in selected:

            self.OpenPosition(
                candidate
            )

    # ==============================================================
    # OUVERTURE D'UNE POSITION
    # ==============================================================

    def OpenPosition(self, candidate):

        symbol = candidate["symbol"]

        features = candidate["features"]

        score = candidate["score"]

        # ----------------------------------------------------------
        # PRIX
        # ----------------------------------------------------------

        price = float(
            features["price"]
        )

        # ----------------------------------------------------------
        # ATR
        # ----------------------------------------------------------

        atr = float(
            features["atr"]
        )

        if price <= 0:

            return

        if atr <= 0:

            return

        # ----------------------------------------------------------
        # CALCUL DE LA QUANTITE
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
        # CONTROLE ALLOCATION
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
        # DEBUG
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
    # FERMETURE D'UNE POSITION
    # ==============================================================

    def ClosePosition(
        self,
        symbol,
        reason
    ):

        # ----------------------------------------------------------
        # VERIFICATION
        # ----------------------------------------------------------

        if not self.Portfolio[
            symbol
        ].Invested:

            return

        # ----------------------------------------------------------
        # INFORMATIONS
        # ----------------------------------------------------------

        quantity = int(
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
        # INFORMATIONS DU TRADE
        # ----------------------------------------------------------

        trade = (
            self.trade_manager
            .GetTrade(
                symbol
            )
        )

        entry_time = trade.entry_time

        entry_score = trade.entry_score

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

        if (
            entry_price > 0
            and
            current_price > 0
        ):

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
        # RESET DU TRADE
        # ----------------------------------------------------------

        self.trade_manager.CloseTrade(
            symbol
        )

        # ----------------------------------------------------------
        # DEBUG
        # ----------------------------------------------------------

        if self.config.DEBUG:

            pnl = (
                current_price
                -
                entry_price
            ) * quantity

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
    # RAPPORT QUOTIDIEN
    # ==============================================================

    def DailyReport(self):

        if self.IsWarmingUp:

            return

        if not self.config.DEBUG:

            return

        # ----------------------------------------------------------
        # REGIME
        # ----------------------------------------------------------

        regime = (
            self.market_regime
            .GetRegime()
        )

        self.Debug(

            "MARKET REGIME | %s"
            %
            regime
        )

        # ----------------------------------------------------------
        # PORTEFEUILLE
        # ----------------------------------------------------------

        self.portfolio_manager.PrintPortfolioReport()

    # ==============================================================
    # FIN DU BACKTEST
    # ==============================================================

    def OnEndOfAlgorithm(self):

        self.statistics.PrintReport()

        self.Debug(

            "FINAL PORTFOLIO VALUE = %.2f"
            %
            self.Portfolio
            .TotalPortfolioValue
        )
