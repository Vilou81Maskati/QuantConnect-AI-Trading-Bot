from AlgorithmImports import *


class StatisticsTracker:

    def __init__(self, algorithm):

        self.algorithm = algorithm

        # ==========================================================
        # HISTORIQUE DES TRADES
        # ==========================================================

        self.trades = []

        # ==========================================================
        # EQUITY
        # ==========================================================

        self.equity_curve = []

        # ==========================================================
        # STATISTIQUES
        # ==========================================================

        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0

        self.gross_profit = 0.0
        self.gross_loss = 0.0

        self.net_profit = 0.0

        self.best_trade = None
        self.worst_trade = None

        self.peak_equity = 0.0
        self.max_drawdown = 0.0

    # ==============================================================
    # MISE A JOUR DE L'EQUITY
    # ==============================================================

    def UpdatePortfolioValue(self):

        value = float(
            self.algorithm.Portfolio
            .TotalPortfolioValue
        )

        self.equity_curve.append({

            "time":
                self.algorithm.Time,

            "value":
                value

        })

        # ----------------------------------------------------------
        # PREMIER PEAK
        # ----------------------------------------------------------

        if self.peak_equity <= 0:

            self.peak_equity = value

        # ----------------------------------------------------------
        # NOUVEAU PEAK
        # ----------------------------------------------------------

        if value > self.peak_equity:

            self.peak_equity = value

        # ----------------------------------------------------------
        # DRAWDOWN
        # ----------------------------------------------------------

        if self.peak_equity > 0:

            drawdown = (
                self.peak_equity
                -
                value
            ) / self.peak_equity

            if drawdown > self.max_drawdown:

                self.max_drawdown = drawdown

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
        reason
    ):

        quantity = abs(
            int(quantity)
        )

        if quantity <= 0:

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
        # RENDEMENT
        # ----------------------------------------------------------

        invested = (
            entry_price
            *
            quantity
        )

        if invested > 0:

            return_pct = (
                pnl
                /
                invested
            )

        else:

            return_pct = 0.0

        # ----------------------------------------------------------
        # TRADE
        # ----------------------------------------------------------

        trade = {

            "symbol":
                symbol.Value,

            "entry_price":
                float(entry_price),

            "exit_price":
                float(exit_price),

            "quantity":
                quantity,

            "pnl":
                float(pnl),

            "return_pct":
                float(return_pct),

            "entry_time":
                entry_time,

            "exit_time":
                exit_time,

            "entry_score":
                int(entry_score),

            "exit_reason":
                reason

        }

        self.trades.append(
            trade
        )

        # ==========================================================
        # STATISTIQUES
        # ==========================================================

        self.total_trades += 1

        self.net_profit += pnl

        # ----------------------------------------------------------
        # TRADE GAGNANT
        # ----------------------------------------------------------

        if pnl > 0:

            self.winning_trades += 1

            self.gross_profit += pnl

        # ----------------------------------------------------------
        # TRADE PERDANT
        # ----------------------------------------------------------

        elif pnl < 0:

            self.losing_trades += 1

            self.gross_loss += abs(
                pnl
            )

        # ----------------------------------------------------------
        # MEILLEUR TRADE
        # ----------------------------------------------------------

        if (
            self.best_trade is None
            or
            pnl > self.best_trade
        ):

            self.best_trade = pnl

        # ----------------------------------------------------------
        # PIRE TRADE
        # ----------------------------------------------------------

        if (
            self.worst_trade is None
            or
            pnl < self.worst_trade
        ):

            self.worst_trade = pnl

    # ==============================================================
    # TAUX DE REUSSITE
    # ==============================================================

    def WinRate(self):

        if self.total_trades <= 0:

            return 0.0

        return (
            self.winning_trades
            /
            self.total_trades
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
    # GAIN MOYEN
    # ==============================================================

    def AverageTrade(self):

        if self.total_trades <= 0:

            return 0.0

        return (
            self.net_profit
            /
            self.total_trades
        )

    # ==============================================================
    # GAIN MOYEN DES GAGNANTS
    # ==============================================================

    def AverageWinner(self):

        if self.winning_trades <= 0:

            return 0.0

        return (
            self.gross_profit
            /
            self.winning_trades
        )

    # ==============================================================
    # PERTE MOYENNE
    # ==============================================================

    def AverageLoser(self):

        if self.losing_trades <= 0:

            return 0.0

        return (
            self.gross_loss
            /
            self.losing_trades
        )

    # ==============================================================
    # RATIO GAIN / PERTE
    # ==============================================================

    def WinLossRatio(self):

        average_loser = (
            self.AverageLoser()
        )

        if average_loser <= 0:

            return 0.0

        return (
            self.AverageWinner()
            /
            average_loser
        )

    # ==============================================================
    # RAPPORT COMPLET
    # ==============================================================

    def GetReport(self):

        portfolio_value = float(
            self.algorithm.Portfolio
            .TotalPortfolioValue
        )

        return {

            "portfolio_value":
                portfolio_value,

            "total_trades":
                self.total_trades,

            "winning_trades":
                self.winning_trades,

            "losing_trades":
                self.losing_trades,

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

            "average_trade":
                self.AverageTrade(),

            "average_winner":
                self.AverageWinner(),

            "average_loser":
                self.AverageLoser(),

            "win_loss_ratio":
                self.WinLossRatio(),

            "best_trade":
                self.best_trade,

            "worst_trade":
                self.worst_trade,

            "max_drawdown":
                self.max_drawdown

        }

    # ==============================================================
    # AFFICHAGE FINAL
    # ==============================================================

    def PrintReport(self):

        report = self.GetReport()

        self.algorithm.Debug(
            "=================================================="
        )

        self.algorithm.Debug(
            "FINAL TRADING REPORT"
        )

        self.algorithm.Debug(
            "=================================================="
        )

        self.algorithm.Debug(

            "Portfolio Value : %.2f"
            %
            report["portfolio_value"]

        )

        self.algorithm.Debug(

            "Total Trades : %d"
            %
            report["total_trades"]

        )

        self.algorithm.Debug(

            "Winning Trades : %d"
            %
            report["winning_trades"]

        )

        self.algorithm.Debug(

            "Losing Trades : %d"
            %
            report["losing_trades"]

        )

        self.algorithm.Debug(

            "Win Rate : %.2f%%"
            %
            (
                report["win_rate"]
                *
                100
            )

        )

        self.algorithm.Debug(

            "Gross Profit : %.2f"
            %
            report["gross_profit"]

        )

        self.algorithm.Debug(

            "Gross Loss : %.2f"
            %
            report["gross_loss"]

        )

        self.algorithm.Debug(

            "Net Profit : %.2f"
            %
            report["net_profit"]

        )

        self.algorithm.Debug(

            "Profit Factor : %.2f"
            %
            report["profit_factor"]

        )

        self.algorithm.Debug(

            "Average Trade : %.2f"
            %
            report["average_trade"]

        )

        self.algorithm.Debug(

            "Average Winner : %.2f"
            %
            report["average_winner"]

        )

        self.algorithm.Debug(

            "Average Loser : %.2f"
            %
            report["average_loser"]

        )

        self.algorithm.Debug(

            "Win/Loss Ratio : %.2f"
            %
            report["win_loss_ratio"]

        )

        self.algorithm.Debug(

            "Best Trade : %.2f"
            %
            (
                report["best_trade"]
                if report["best_trade"] is not None
                else 0.0
            )

        )

        self.algorithm.Debug(

            "Worst Trade : %.2f"
            %
            (
                report["worst_trade"]
                if report["worst_trade"] is not None
                else 0.0
            )

        )

        self.algorithm.Debug(

            "Maximum Drawdown : %.2f%%"
            %
            (
                report["max_drawdown"]
                *
                100
            )

        )

        self.algorithm.Debug(
            "=================================================="
        )
