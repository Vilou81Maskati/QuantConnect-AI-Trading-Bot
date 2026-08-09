"""
Module de statistiques et de suivi des performances.

Ce module ne prend aucune décision de trading.
Il collecte uniquement les résultats afin de pouvoir évaluer
objectivement la stratégie pendant les backtests.
"""

from AlgorithmImports import *


class TradeRecord:

    def __init__(
        self,
        symbol,
        entry_price,
        exit_price,
        quantity,
        pnl,
        pnl_percent,
        entry_time,
        exit_time,
        entry_score,
        exit_reason
    ):

        self.symbol = symbol

        self.entry_price = entry_price

        self.exit_price = exit_price

        self.quantity = quantity

        self.pnl = pnl

        self.pnl_percent = pnl_percent

        self.entry_time = entry_time

        self.exit_time = exit_time

        self.entry_score = entry_score

        self.exit_reason = exit_reason


class StatisticsTracker:

    def __init__(
        self,
        algorithm
    ):

        self.algorithm = algorithm

        # ==========================================================
        # COMPTEURS
        # ==========================================================

        self.total_trades = 0

        self.winning_trades = 0

        self.losing_trades = 0

        self.break_even_trades = 0

        # ==========================================================
        # RESULTATS
        # ==========================================================

        self.gross_profit = 0.0

        self.gross_loss = 0.0

        self.net_profit = 0.0

        # ==========================================================
        # SERIES
        # ==========================================================

        self.trade_records = []

        self.daily_values = []

        # ==========================================================
        # RISQUE
        # ==========================================================

        self.peak_value = 0.0

        self.max_drawdown = 0.0

        # ==========================================================
        # INITIALISATION
        # ==========================================================

        self.peak_value = (
            float(
                algorithm
                .Portfolio
                .TotalPortfolioValue
            )
        )

    # ==============================================================
    # ENREGISTREMENT D'UN TRADE
    # ==============================================================

    def RecordTrade(
        self,
        symbol,
        entry_price,
        exit_price,
        quantity,
        entry_time,
        exit_time,
        entry_score,
        exit_reason
    ):

        if entry_price <= 0:

            return

        if quantity == 0:

            return

        # ----------------------------------------------------------
        # PNL
        # ----------------------------------------------------------

        pnl = (
            exit_price
            -
            entry_price
        ) * quantity

        # ----------------------------------------------------------
        # POURCENTAGE
        # ----------------------------------------------------------

        invested_capital = (
            entry_price
            *
            abs(quantity)
        )

        if invested_capital > 0:

            pnl_percent = (
                pnl
                /
                invested_capital
            )

        else:

            pnl_percent = 0.0

        # ----------------------------------------------------------
        # COMPTEUR
        # ----------------------------------------------------------

        self.total_trades += 1

        # ----------------------------------------------------------
        # GAIN
        # ----------------------------------------------------------

        if pnl > 0:

            self.winning_trades += 1

            self.gross_profit += pnl

        # ----------------------------------------------------------
        # PERTE
        # ----------------------------------------------------------

        elif pnl < 0:

            self.losing_trades += 1

            self.gross_loss += abs(pnl)

        # ----------------------------------------------------------
        # BREAK EVEN
        # ----------------------------------------------------------

        else:

            self.break_even_trades += 1

        # ----------------------------------------------------------
        # RESULTAT NET
        # ----------------------------------------------------------

        self.net_profit += pnl

        # ----------------------------------------------------------
        # ENREGISTREMENT
        # ----------------------------------------------------------

        record = TradeRecord(

            symbol,

            entry_price,

            exit_price,

            quantity,

            pnl,

            pnl_percent,

            entry_time,

            exit_time,

            entry_score,

            exit_reason
        )

        self.trade_records.append(
            record
        )

    # ==============================================================
    # VALEUR DU PORTEFEUILLE
    # ==============================================================

    def UpdatePortfolioValue(self):

        value = (
            float(
                self.algorithm
                .Portfolio
                .TotalPortfolioValue
            )
        )

        self.daily_values.append(

            (
                self.algorithm.Time,
                value
            )
        )

        # ----------------------------------------------------------
        # NOUVEAU PLUS HAUT
        # ----------------------------------------------------------

        if value > self.peak_value:

            self.peak_value = value

        # ----------------------------------------------------------
        # DRAWDOWN
        # ----------------------------------------------------------

        if self.peak_value > 0:

            drawdown = (
                self.peak_value
                -
                value
            ) / self.peak_value

            if drawdown > self.max_drawdown:

                self.max_drawdown = drawdown

    # ==============================================================
    # TAUX DE REUSSITE
    # ==============================================================

    def WinRate(self):

        if self.total_trades == 0:

            return 0.0

        return (
            self.winning_trades
            /
            self.total_trades
        )

    # ==============================================================
    # GAIN MOYEN
    # ==============================================================

    def AverageWin(self):

        if self.winning_trades == 0:

            return 0.0

        return (
            self.gross_profit
            /
            self.winning_trades
        )

    # ==============================================================
    # PERTE MOYENNE
    # ==============================================================

    def AverageLoss(self):

        if self.losing_trades == 0:

            return 0.0

        return (
            self.gross_loss
            /
            self.losing_trades
        )

    # ==============================================================
    # PROFIT FACTOR
    # ==============================================================

    def ProfitFactor(self):

        if self.gross_loss <= 0:

            return 0.0

        return (
            self.gross_profit
            /
            self.gross_loss
        )

    # ==============================================================
    # PAYOFF RATIO
    # ==============================================================

    def PayoffRatio(self):

        average_loss = (
            self.AverageLoss()
        )

        if average_loss <= 0:

            return 0.0

        return (
            self.AverageWin()
            /
            average_loss
        )

    # ==============================================================
    # EXPECTANCY
    # ==============================================================

    def Expectancy(self):

        if self.total_trades == 0:

            return 0.0

        win_probability = (
            self.WinRate()
        )

        loss_probability = (
            self.losing_trades
            /
            self.total_trades
        )

        average_win = (
            self.AverageWin()
        )

        average_loss = (
            self.AverageLoss()
        )

        expectancy = (

            win_probability
            *
            average_win

            -

            loss_probability
            *
            average_loss
        )

        return expectancy

    # ==============================================================
    # RENDEMENT TOTAL
    # ==============================================================

    def TotalReturn(self):

        initial = (
            self.algorithm
            .Portfolio
            .TotalPortfolioValue
        )

        if initial <= 0:

            return 0.0

        return (
            self.net_profit
            /
            initial
        )

    # ==============================================================
    # RAPPORT GLOBAL
    # ==============================================================

    def GetReport(self):

        return {

            "total_trades":
                self.total_trades,

            "winning_trades":
                self.winning_trades,

            "losing_trades":
                self.losing_trades,

            "break_even_trades":
                self.break_even_trades,

            "win_rate":
                self.WinRate(),

            "gross_profit":
                self.gross_profit,

            "gross_loss":
                self.gross_loss,

            "net_profit":
                self.net_profit,

            "profit_factor":
                self.ProfitFactor(),

            "average_win":
                self.AverageWin(),

            "average_loss":
                self.AverageLoss(),

            "payoff_ratio":
                self.PayoffRatio(),

            "expectancy":
                self.Expectancy(),

            "max_drawdown":
                self.max_drawdown
        }

    # ==============================================================
    # AFFICHAGE DES STATISTIQUES
    # ==============================================================

    def PrintReport(self):

        report = (
            self.GetReport()
        )

        self.algorithm.Debug(
            "================================================"
        )

        self.algorithm.Debug(
            "             STRATEGY REPORT"
        )

        self.algorithm.Debug(
            "================================================"
        )

        self.algorithm.Debug(
            "Trades       : %d"
            %
            report["total_trades"]
        )

        self.algorithm.Debug(
            "Wins         : %d"
            %
            report["winning_trades"]
        )

        self.algorithm.Debug(
            "Losses       : %d"
            %
            report["losing_trades"]
        )

        self.algorithm.Debug(
            "Win rate     : %.2f %%"
            %
            (
                report["win_rate"]
                *
                100
            )
        )

        self.algorithm.Debug(
            "Gross profit : %.2f"
            %
            report["gross_profit"]
        )

        self.algorithm.Debug(
            "Gross loss   : %.2f"
            %
            report["gross_loss"]
        )

        self.algorithm.Debug(
            "Net profit   : %.2f"
            %
            report["net_profit"]
        )

        self.algorithm.Debug(
            "Profit factor: %.2f"
            %
            report["profit_factor"]
        )

        self.algorithm.Debug(
            "Average win  : %.2f"
            %
            report["average_win"]
        )

        self.algorithm.Debug(
            "Average loss : %.2f"
            %
            report["average_loss"]
        )

        self.algorithm.Debug(
            "Payoff ratio : %.2f"
            %
            report["payoff_ratio"]
        )

        self.algorithm.Debug(
            "Expectancy   : %.2f"
            %
            report["expectancy"]
        )

        self.algorithm.Debug(
            "Max drawdown : %.2f %%"
            %
            (
                report["max_drawdown"]
                *
                100
            )
        )

        self.algorithm.Debug(
            "================================================"
        )

    # ==============================================================
    # STATISTIQUES PAR ACTIF
    # ==============================================================

    def SymbolStatistics(
        self,
        symbol
    ):

        trades = [

            trade

            for trade
            in self.trade_records

            if trade.symbol == symbol
        ]

        if not trades:

            return None

        wins = [

            trade
            for trade
            in trades

            if trade.pnl > 0
        ]

        losses = [

            trade
            for trade
            in trades

            if trade.pnl < 0
        ]

        gross_profit = sum(

            trade.pnl

            for trade
            in wins
        )

        gross_loss = sum(

            abs(trade.pnl)

            for trade
            in losses
        )

        profit_factor = 0.0

        if gross_loss > 0:

            profit_factor = (
                gross_profit
                /
                gross_loss
            )

        return {

            "trades":
                len(trades),

            "wins":
                len(wins),

            "losses":
                len(losses),

            "net_profit":
                sum(
                    trade.pnl
                    for trade
                    in trades
                ),

            "profit_factor":
                profit_factor
        }
