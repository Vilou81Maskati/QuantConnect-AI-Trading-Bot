from AlgorithmImports import *


class TradeState:

    def __init__(
        self,
        symbol,
        entry_price,
        entry_atr,
        entry_score,
        entry_time,
        tag
    ):

        self.symbol = symbol

        self.entry_price = float(
            entry_price
        )

        self.entry_atr = float(
            entry_atr
        )

        self.entry_score = int(
            entry_score
        )

        self.entry_time = entry_time

        self.tag = tag

        # ----------------------------------------------------------
        # STOP INITIAL
        # ----------------------------------------------------------

        self.initial_stop = (
            self.entry_price
            -
            (
                self.entry_atr
                *
                2.0
            )
        )

        self.stop_price = (
            self.initial_stop
        )

        # ----------------------------------------------------------
        # OBJECTIF INITIAL
        # ----------------------------------------------------------

        self.target_price = (
            self.entry_price
            +
            (
                self.entry_atr
                *
                4.0
            )
        )

        # ----------------------------------------------------------
        # PLUS HAUT PRIX
        # ----------------------------------------------------------

        self.highest_price = (
            self.entry_price
        )

        # ----------------------------------------------------------
        # TRAILING
        # ----------------------------------------------------------

        self.trailing_stop = None

        self.is_active = True


class TradeManager:

    def __init__(
        self,
        algorithm,
        config
    ):

        self.algorithm = algorithm

        self.config = config

        self.trades = {}

    # ==============================================================
    # ENREGISTREMENT D'UNE ENTREE
    # ==============================================================

    def RegisterEntry(
        self,
        symbol,
        entry_price,
        atr,
        score,
        tag
    ):

        trade = TradeState(

            symbol,

            entry_price,

            atr,

            score,

            self.algorithm.Time,

            tag
        )

        # ----------------------------------------------------------
        # PARAMETRES CONFIGURATION
        # ----------------------------------------------------------

        trade.initial_stop = (
            entry_price
            -
            (
                atr
                *
                self.config.STOP_ATR_MULTIPLIER
            )
        )

        trade.stop_price = (
            trade.initial_stop
        )

        trade.target_price = (
            entry_price
            +
            (
                atr
                *
                self.config.TARGET_ATR_MULTIPLIER
            )
        )

        self.trades[symbol] = trade

    # ==============================================================
    # RECUPERATION D'UN TRADE
    # ==============================================================

    def GetTrade(
        self,
        symbol
    ):

        return self.trades.get(
            symbol,
            None
        )

    # ==============================================================
    # MISE A JOUR
    # ==============================================================

    def UpdateTrade(
        self,
        symbol,
        price,
        atr
    ):

        trade = self.GetTrade(
            symbol
        )

        if trade is None:

            return

        if not trade.is_active:

            return

        if price <= 0:

            return

        if atr <= 0:

            return

        # ----------------------------------------------------------
        # NOUVEAU PLUS HAUT
        # ----------------------------------------------------------

        if price > trade.highest_price:

            trade.highest_price = price

        # ----------------------------------------------------------
        # TRAILING STOP
        # ----------------------------------------------------------

        trailing_distance = (
            atr
            *
            self.config.TRAILING_ATR_MULTIPLIER
        )

        proposed_trailing = (
            trade.highest_price
            -
            trailing_distance
        )

        # ----------------------------------------------------------
        # LE TRAILING NE PEUT PAS DESCENDRE
        # ----------------------------------------------------------

        if trade.trailing_stop is None:

            trade.trailing_stop = (
                proposed_trailing
            )

        else:

            trade.trailing_stop = max(

                trade.trailing_stop,

                proposed_trailing

            )

        # ----------------------------------------------------------
        # LE STOP FINAL EST LE PLUS ELEVE
        # ----------------------------------------------------------

        trade.stop_price = max(

            trade.stop_price,

            trade.trailing_stop

        )

        # ----------------------------------------------------------
        # PASSAGE EN PROTECTION DU CAPITAL
        # ----------------------------------------------------------

        profit_distance = (
            trade.entry_price
            *
            0.01
        )

        if (
            price
            >=
            trade.entry_price
            +
            profit_distance
        ):

            # ------------------------------------------------------
            # STOP AU-DESSUS DU PRIX D'ENTREE
            # ------------------------------------------------------

            break_even_stop = (
                trade.entry_price
            )

            trade.stop_price = max(

                trade.stop_price,

                break_even_stop

            )

    # ==============================================================
    # VERIFICATION DE SORTIE
    # ==============================================================

    def CheckExit(
        self,
        symbol,
        features,
        signal_engine
    ):

        trade = self.GetTrade(
            symbol
        )

        if trade is None:

            return None

        if not trade.is_active:

            return None

        if features is None:

            return None

        price = float(
            features["price"]
        )

        if price <= 0:

            return None

        # ----------------------------------------------------------
        # STOP LOSS
        # ----------------------------------------------------------

        if price <= trade.stop_price:

            return "STOP_LOSS"

        # ----------------------------------------------------------
        # TAKE PROFIT
        # ----------------------------------------------------------

        if price >= trade.target_price:

            return "TAKE_PROFIT"

        # ----------------------------------------------------------
        # SIGNAL TECHNIQUE
        # ----------------------------------------------------------

        if signal_engine.IsExitSignal(
            features
        ):

            return "SIGNAL_EXIT"

        return None

    # ==============================================================
    # FERMETURE
    # ==============================================================

    def CloseTrade(
        self,
        symbol
    ):

        trade = self.GetTrade(
            symbol
        )

        if trade is None:

            return

        trade.is_active = False

        del self.trades[
            symbol
        ]

    # ==============================================================
    # VERIFICATION EXISTENCE
    # ==============================================================

    def HasTrade(
        self,
        symbol
    ):

        return symbol in self.trades

    # ==============================================================
    # NOMBRE DE TRADES
    # ==============================================================

    def ActiveTradeCount(self):

        return len(
            self.trades
        )

    # ==============================================================
    # INFORMATIONS DU TRADE
    # ==============================================================

    def GetTradeReport(
        self,
        symbol
    ):

        trade = self.GetTrade(
            symbol
        )

        if trade is None:

            return None

        return {

            "symbol":
                symbol.Value,

            "entry_price":
                trade.entry_price,

            "stop_price":
                trade.stop_price,

            "target_price":
                trade.target_price,

            "highest_price":
                trade.highest_price,

            "trailing_stop":
                trade.trailing_stop,

            "entry_score":
                trade.entry_score,

            "entry_time":
                trade.entry_time,

            "active":
                trade.is_active

        }
