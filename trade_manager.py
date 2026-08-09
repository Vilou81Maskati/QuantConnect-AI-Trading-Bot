"""
Gestionnaire des positions.

Responsabilités :
- mémoriser les caractéristiques d'une position ;
- calculer et mettre à jour le stop ;
- gérer l'objectif ;
- gérer le trailing stop ;
- déterminer une raison de sortie ;
- nettoyer l'état après fermeture.

Important :
Le TradeManager ne passe pas directement les ordres.
La décision d'exécuter un ordre reste dans main.py.
"""

from AlgorithmImports import *


class TradeState:

    def __init__(self, symbol):

        self.symbol = symbol

        # ----------------------------------------------------------
        # ETAT DE LA POSITION
        # ----------------------------------------------------------

        self.active = False

        # ----------------------------------------------------------
        # PRIX
        # ----------------------------------------------------------

        self.entry_price = 0.0

        self.current_price = 0.0

        self.highest_price = 0.0

        # ----------------------------------------------------------
        # RISQUE
        # ----------------------------------------------------------

        self.initial_stop = 0.0

        self.stop_price = 0.0

        self.target_price = 0.0

        # ----------------------------------------------------------
        # ATR
        # ----------------------------------------------------------

        self.entry_atr = 0.0

        self.current_atr = 0.0

        # ----------------------------------------------------------
        # TEMPS
        # ----------------------------------------------------------

        self.entry_time = None

        self.last_update = None

        # ----------------------------------------------------------
        # INFORMATIONS
        # ----------------------------------------------------------

        self.entry_score = 0

        self.entry_tag = ""

    # ==============================================================
    # INITIALISATION DU TRADE
    # ==============================================================

    def Open(
        self,
        price,
        atr,
        target_multiplier,
        stop_multiplier,
        score,
        tag,
        current_time
    ):

        self.active = True

        self.entry_price = price

        self.current_price = price

        self.highest_price = price

        self.entry_atr = atr

        self.current_atr = atr

        # ----------------------------------------------------------
        # STOP INITIAL
        # ----------------------------------------------------------

        self.initial_stop = (
            price
            -
            atr
            *
            stop_multiplier
        )

        self.stop_price = (
            self.initial_stop
        )

        # ----------------------------------------------------------
        # OBJECTIF
        # ----------------------------------------------------------

        self.target_price = (
            price
            +
            atr
            *
            target_multiplier
        )

        # ----------------------------------------------------------
        # INFORMATIONS
        # ----------------------------------------------------------

        self.entry_time = current_time

        self.last_update = current_time

        self.entry_score = score

        self.entry_tag = tag

    # ==============================================================
    # MISE A JOUR
    # ==============================================================

    def Update(
        self,
        price,
        atr,
        current_time
    ):

        if not self.active:

            return

        self.current_price = price

        self.current_atr = atr

        self.last_update = current_time

        # ----------------------------------------------------------
        # NOUVEAU PLUS HAUT
        # ----------------------------------------------------------

        if price > self.highest_price:

            self.highest_price = price

    # ==============================================================
    # TRAILING STOP
    # ==============================================================

    def UpdateTrailingStop(
        self,
        atr,
        multiplier
    ):

        if not self.active:

            return

        if atr <= 0:

            return

        # ----------------------------------------------------------
        # NOUVEAU STOP THEORIQUE
        # ----------------------------------------------------------

        trailing_stop = (
            self.highest_price
            -
            atr
            *
            multiplier
        )

        # ----------------------------------------------------------
        # LE STOP NE DOIT JAMAIS REDESCENDRE
        # ----------------------------------------------------------

        if (
            trailing_stop
            >
            self.stop_price
        ):

            self.stop_price = (
                trailing_stop
            )

    # ==============================================================
    # VERIFICATION DU STOP
    # ==============================================================

    def StopHit(self):

        if not self.active:

            return False

        if self.current_price <= self.stop_price:

            return True

        return False

    # ==============================================================
    # VERIFICATION DE L'OBJECTIF
    # ==============================================================

    def TargetHit(self):

        if not self.active:

            return False

        if self.current_price >= self.target_price:

            return True

        return False

    # ==============================================================
    # RENDEMENT
    # ==============================================================

    def ReturnPercent(self):

        if self.entry_price <= 0:

            return 0.0

        return (
            self.current_price
            -
            self.entry_price
        ) / self.entry_price

    # ==============================================================
    # DISTANCE DU STOP
    # ==============================================================

    def StopDistancePercent(self):

        if self.entry_price <= 0:

            return 0.0

        return (
            self.entry_price
            -
            self.stop_price
        ) / self.entry_price

    # ==============================================================
    # VERIFICATION DE SORTIE
    # ==============================================================

    def CheckExit(
        self,
        features,
        signal_engine
    ):

        if not self.active:

            return None

        # ----------------------------------------------------------
        # STOP
        # ----------------------------------------------------------

        if self.StopHit():

            return "STOP_LOSS"

        # ----------------------------------------------------------
        # OBJECTIF
        # ----------------------------------------------------------

        if self.TargetHit():

            return "TARGET"

        # ----------------------------------------------------------
        # SIGNAL STRATEGIQUE
        # ----------------------------------------------------------

        if features is not None:

            signal = (
                signal_engine.GetExitSignal(
                    features,
                    self.entry_price
                )
            )

            if signal.value == "EXIT":

                return "STRATEGY_EXIT"

        return None

    # ==============================================================
    # FERMETURE
    # ==============================================================

    def Close(self):

        self.active = False

    # ==============================================================
    # RESET COMPLET
    # ==============================================================

    def Reset(self):

        symbol = self.symbol

        self.__init__(
            symbol
        )


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
    # RECUPERER OU CREER UN TRADE
    # ==============================================================

    def GetTrade(
        self,
        symbol
    ):

        if symbol not in self.trades:

            self.trades[symbol] = (
                TradeState(symbol)
            )

        return self.trades[symbol]

    # ==============================================================
    # OUVERTURE
    # ==============================================================

    def RegisterEntry(
        self,
        symbol,
        price,
        atr,
        score,
        tag
    ):

        trade = self.GetTrade(
            symbol
        )

        trade.Open(

            price,

            atr,

            self.config.TARGET_ATR_MULTIPLIER,

            self.config.STOP_ATR_MULTIPLIER,

            score,

            tag,

            self.algorithm.Time
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

        if not trade.active:

            return

        trade.Update(

            price,

            atr,

            self.algorithm.Time
        )

        trade.UpdateTrailingStop(

            atr,

            self.config.TRAILING_ATR_MULTIPLIER
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

        return trade.CheckExit(

            features,

            signal_engine
        )

    # ==============================================================
    # POSITION ACTIVE
    # ==============================================================

    def IsActive(
        self,
        symbol
    ):

        trade = self.GetTrade(
            symbol
        )

        return trade.active

    # ==============================================================
    # PRIX D'ENTREE
    # ==============================================================

    def EntryPrice(
        self,
        symbol
    ):

        trade = self.GetTrade(
            symbol
        )

        return trade.entry_price

    # ==============================================================
    # STOP
    # ==============================================================

    def StopPrice(
        self,
        symbol
    ):

        trade = self.GetTrade(
            symbol
        )

        return trade.stop_price

    # ==============================================================
    # OBJECTIF
    # ==============================================================

    def TargetPrice(
        self,
        symbol
    ):

        trade = self.GetTrade(
            symbol
        )

        return trade.target_price

    # ==============================================================
    # RENDEMENT
    # ==============================================================

    def ReturnPercent(
        self,
        symbol
    ):

        trade = self.GetTrade(
            symbol
        )

        return trade.ReturnPercent()

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

        trade.Close()

        trade.Reset()

    # ==============================================================
    # RAPPORT D'UNE POSITION
    # ==============================================================

    def GetTradeReport(
        self,
        symbol
    ):

        trade = self.GetTrade(
            symbol
        )

        return {

            "symbol":
                symbol.Value,

            "active":
                trade.active,

            "entry_price":
                trade.entry_price,

            "current_price":
                trade.current_price,

            "stop":
                trade.stop_price,

            "target":
                trade.target_price,

            "highest":
                trade.highest_price,

            "return":
                trade.ReturnPercent(),

            "score":
                trade.entry_score,

            "entry_time":
                trade.entry_time
        }
