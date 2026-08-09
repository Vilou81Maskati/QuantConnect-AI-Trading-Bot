from AlgorithmImports import *

class UniverseManager:

    def __init__(self, algorithm):

        self.algorithm = algorithm

        self.symbols = []

    def Initialize(self, tickers):

        for ticker in tickers:

            symbol = self.algorithm.AddEquity(

                ticker,

                Resolution.Hour

            ).Symbol

            self.symbols.append(symbol)

    def GetUniverse(self):

        return self.symbols
