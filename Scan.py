import time

import alpaca_trade_api
from KEYS import *
import datetime
import pprint
import json
import sys
import requests


class Scan:
    alpacaAPI = alpaca_trade_api.REST(ALPACA_PUBLIC_KEY, ALPACA_PRIVATE_KEY, api_version="v2")
    alpacaDateTimeFormat = "%Y-%m-%dT%H:%M:%S"

    def __init__(self, symbol):
        self.symbol = symbol
        self.currentTime = datetime.datetime.now()
        self.testingTime = datetime.datetime(2020, 6, 29, 14, 23)
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
        self.currentTrade = None #trade object trade object needs to change this variable when in closes itself.
        self.bias = None

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
        toPositive = lambda x: x * -1
        subNoNegatives = lambda x, y: max(x, y) - min(x, y)
        print("here")
        barSize = subNoNegatives(self.latestCandle.o, self.latestCandle.c)
        minimumReq = barSize * 0.501


        self.SMA = sum(self.lastXClosingPrices) / len(self.lastXClosingPrices)

        smaHeight = subNoNegatives(self.SMA, self.latestCandle.c)
        insideSMA = True
        completelyAbove = completelyBelow = None

        if smaHeight > barSize or smaHeight < 0:
            print("out of bounds")
            insideSMA = False
            # above = smaHeight < 0
            # below = not above
        completelyAbove = min(self.latestCandle.o, self.latestCandle.c) > self.SMA
        completelyBelow = max(self.latestCandle.o, self.latestCandle.c) < self.SMA
        print(self.latestCandle)
        print(self.SMA)
        print(self.SMA - min(self.latestCandle.c, self.latestCandle.o))
        print(max(self.latestCandle.c , self.latestCandle.o) - self.SMA)

        if insideSMA:
            if self.SMA - min(self.latestCandle.c, self.latestCandle.o) > max(self.latestCandle.c , self.latestCandle.o) - self.SMA:
                return "bear"
            else:
                return "bull"
        elif completelyAbove:
            return "bull"
        elif completelyBelow:
            return "bear"
        else:
            print("caught")

    def onTick(self):
        # once awake, check prices, get new SMA, check for a signal
        self.lastXClosingPrices = self.getClosingPrices(10)
        self.latestCandle = Scan.alpacaAPI.get_barset(symbols=self.symbol, limit=1, end="{}-04:00".format(self.testingTime.strftime(Scan.alpacaDateTimeFormat)), timeframe="minute")[self.symbol][0]
        self.lastXClosingPrices.pop(0)
        self.lastXClosingPrices.append(self.latestCandle.c)
        self.bias = self.isSignal()
        print(self.bias)
        if self.bias == "bull":
            if not self.openTrade:
                #open trade
                pass
            elif self.currentTrade != self.bias: #.side #.isOpen
                #close position and open opposing position
                pass
            # sleep to next minute on conformation of trade
        elif "bear":  # do somethings else, proably slee
            # can probably be done in one block
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
