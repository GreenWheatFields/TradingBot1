import time

import alpaca_trade_api
from KEYS import *
import datetime
from Trade import Trade
import json
import sys
import requests


class Scan:
    alpacaAPI = alpaca_trade_api.REST(ALPACA_PUBLIC_KEY, ALPACA_PRIVATE_KEY, api_version="v2")
    alpacaDateTimeFormat = "%Y-%m-%dT%H:%M:%S"

    def __init__(self, symbol):
        self.symbol = symbol
        self.currentTime = datetime.datetime.now()
        self.testingTime = datetime.datetime(2020, 6, 29, 14, 4)
        self.isMarketOpen = True
        self.nextOpen = None
        self.nextClose = None
        self.SMA = None
        self.SMAlist = None
        self.lastXCandles = None
        self.openTrade = False
        self.candleColor = None
        self.latestCandle = None
        self.lastXClosingPrices = None
        self.currentTrade = None  # trade object trade object needs to change this variable when in closes itself.
        self.bias = None
        self.api = alpacaAPI = alpaca_trade_api.REST(ALPACA_PUBLIC_KEY, ALPACA_PRIVATE_KEY, api_version="v2")

    def lookForTrades(self):
        if self.isMarketOpen:
            # while self.currentTime.second != 0:
            #     print("waitng")
            #     print(self.currentTime)
            #     self.currentTime = datetime.datetime.now()
            print(self.testingTime)
            self.onTick()
            # self.candleColor = "red" if self.lastXCandles.o > self.lastXCandles.c else "green"

        else:
            self.checkMarketConditions()

    def isSignal(self):
        self.SMA = sum(self.lastXClosingPrices) / len(self.lastXClosingPrices)
        insideSMA = False if self.SMA > max(self.latestCandle.c, self.latestCandle.o) or self.SMA < min(self.latestCandle.c, self.latestCandle.o) else True

        completelyAbove = min(self.latestCandle.o, self.latestCandle.c) > self.SMA
        completelyBelow = max(self.latestCandle.o, self.latestCandle.c) < self.SMA

        if insideSMA:
            if self.SMA - min(self.latestCandle.c, self.latestCandle.o) > max(self.latestCandle.c, self.latestCandle.o) - self.SMA:
                return "bear"
            else:
                return "bull"
        elif completelyAbove:
            return "bull"
        elif completelyBelow:
            return "bear"
        else:
            # todo, handle exception
            print("caught")

    def onTick(self):
        # once awake, check prices, get new SMA, check for a signal
        self.lastXClosingPrices = self.getClosingPrices(10)
        self.latestCandle = \
        Scan.alpacaAPI.get_barset(symbols=self.symbol, limit=1, end="{}-04:00".format(self.testingTime.strftime(Scan.alpacaDateTimeFormat)), timeframe="minute")[self.symbol][0]
        self.lastXClosingPrices.pop(0)
        self.lastXClosingPrices.append(self.latestCandle.c)
        self.bias = self.isSignal()
        print(self.bias)
        if not self.openTrade:
            # not sure how this interaction works, when a trade closes itself, can it still be refernced?
            self.currentTrade = Trade(self.bias, self, "trailingStop", Scan.alpacaAPI)
            self.currentTrade.open()
            while not self.currentTrade.filled:
                # do something
                pass

        elif self.openTrade and self.currentTrade.bias != self.bias:
            self.currentTrade.close()

        elif self.openTrade and self.currentTrade.bias == self.bias:
            # do nothing
            pass

    def checkMarketConditions(self):
        response = Scan.alpacaAPI.get_clock()
        self.isMarketOpen = response.is_open
        self.nextOpen = response.next_open
        self.nextClose = response.next_close

    def getClosingPrices(self, amount: int) -> list:
        timedelta = datetime.timedelta(minutes=1)
        candles = Scan.alpacaAPI.get_barset(symbols=self.symbol, limit=amount, end="{}-04:00".format((self.testingTime - timedelta).strftime(Scan.alpacaDateTimeFormat)),
                                            timeframe="minute")[self.symbol]
        return [i.c for i in candles]

    @staticmethod
    def KillSwitch(self):
        pass


if __name__ == '__main__':
    scan = Scan("SPY")
    scan.lookForTrades()
