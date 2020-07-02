import time

import alpaca_trade_api
from KEYS import *
import datetime
from Trade import Trade
import json
import sys
import requests
import os


class Scan:
    os.environ["APCA_API_BASE_URL"] = "https://paper-api.alpaca.markets"
    alpacaAPI = alpaca_trade_api.REST(ALPACA_PUBLIC_KEY, ALPACA_PRIVATE_KEY, api_version="v2")
    alpacaDateTimeFormat = "%Y-%m-%dT%H:%M:%S"
    print(os.getenv("APCA_API_BASE_URL"))

    def __init__(self, symbol):
        self.symbol = symbol
        self.currentTime = datetime.datetime.now()
        self.testingTime = datetime.datetime(2020, 6, 29, 14, 4)
        self.testingTime = self.currentTime
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
            while self.isMarketOpen:
                self.onTick()
                print("sleeping")
                sleeptime = 60 - datetime.datetime.utcnow().second
                time.sleep(sleeptime + 1)


        else:
            self.checkMarketConditions()

    def isSignal(self):
        self.SMA = sum(self.lastXClosingPrices) / len(self.lastXClosingPrices)
        insideSMA = False if self.SMA > max(self.latestCandle.c, self.latestCandle.o) or self.SMA < min(
            self.latestCandle.c, self.latestCandle.o) else True

        completelyAbove = min(self.latestCandle.o, self.latestCandle.c) > self.SMA
        completelyBelow = max(self.latestCandle.o, self.latestCandle.c) < self.SMA
        print("SMA", self.SMA)
        print("completelyAbove", completelyAbove)
        print("completlybelow", completelyBelow)
        if insideSMA:
            if self.SMA - min(self.latestCandle.c, self.latestCandle.o) > max(self.latestCandle.c,
                                                                              self.latestCandle.o) - self.SMA:
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
        print(self.lastXClosingPrices)
        self.latestCandle = \
            Scan.alpacaAPI.get_barset(symbols=self.symbol, limit=1,
                                      end="{}-04:00".format(self.testingTime.strftime(Scan.alpacaDateTimeFormat)),
                                      timeframe="minute")[self.symbol][0]

        self.lastXClosingPrices.pop(0)
        self.lastXClosingPrices.append(self.latestCandle.c)
        print(self.lastXClosingPrices)
        print(self.latestCandle)
        print(self.latestCandle.t)
        print(self.testingTime)
        self.bias = self.isSignal()
        print(self.bias)
        if not self.openTrade:
            self.currentTrade = Trade(self, Scan.alpacaAPI, self.bias)
            self.currentTrade.open()
            self.openTrade = True
            print("opening trade")
            return
        elif self.openTrade and self.currentTrade.bias != self.bias:
            self.currentTrade.close()
            self.currentTrade = Trade(self, Scan.alpacaAPI, self.bias)
            self.currentTrade.open()
            print("bear trade")
            return
        else:
            print("doing nothing")
            return

    def checkMarketConditions(self):
        response = Scan.alpacaAPI.get_clock()
        self.isMarketOpen = response.is_open
        self.nextOpen = response.next_open
        self.nextClose = response.next_close

    def getClosingPrices(self, amount: int) -> list:
        timedelta = datetime.timedelta(minutes=1)
        candles = Scan.alpacaAPI.get_barset(symbols=self.symbol, limit=amount, end="{}-04:00".format(
            (self.testingTime - timedelta).strftime(Scan.alpacaDateTimeFormat)),
                                            timeframe="minute")[self.symbol]
        return [i.c for i in candles]

    @staticmethod
    def KillSwitch(self):
        pass

    def start(self):
        print("waiting for next full minute to get data")
        sleeptime = 60 - datetime.datetime.utcnow().second
        time.sleep(sleeptime + 1)
        self.lookForTrades()



if __name__ == '__main__':
    scan = Scan("SPY")
    scan.start()
