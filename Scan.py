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

    def __init__(self, symbol):
        self.symbol = symbol
        self.currentTime = datetime.datetime.now()
        self.testingTime = datetime.datetime(2020, 7, 2, 9, 45)
        self.testingTime = self.currentTime
        self.isMarketOpen = True
        # self.nextOpen = None
        # self.nextClose = None
        self.SMA = None
        self.openTrade = False
        self.candleColor = None
        self.latestCandle = None
        self.lastXClosingPrices = None
        self.currentTrade = None
        self.bias = None
        self.api = alpacaAPI = alpaca_trade_api.REST(ALPACA_PUBLIC_KEY, ALPACA_PRIVATE_KEY, api_version="v2")

    def lookForTrades(self):
        if self.isMarketOpen:
            while self.isMarketOpen:
                self.onTick()
                print("master thread sleeping")
                self.sleepTillNextMinute()
                # time.sleep(2)
                # self.testingTime += datetime.timedelta(minutes=1)
        else:
            self.checkMarketConditions()

    def onTick(self):
        # once awake, check prices, get new SMA, check for a signal
        self.lastXClosingPrices = self.getClosingPrices(10)
        self.latestCandle = \
        Scan.alpacaAPI.get_barset(symbols=self.symbol, limit=1, end="{}-04:00".format(self.testingTime.strftime(Scan.alpacaDateTimeFormat)), timeframe="minute")[self.symbol][0]
        self.lastXClosingPrices.pop(0)
        self.lastXClosingPrices.append(self.latestCandle.c)
        self.bias = self.isSignal()
        print(self.bias)
        if self.currentTrade is None:
            print("master opening trade", self.bias)
            self.currentTrade = Trade(self, Scan.alpacaAPI, self.bias)
            self.currentTrade.start()
            print("here")
            return
        elif self.currentTrade.bias != self.bias:
            print("master reversed trade", self.bias)
            self.currentTrade.interrupt()
            self.currentTrade.close()
            self.currentTrade = Trade(self, Scan.alpacaAPI, self.bias)
            self.currentTrade.openAndMonitor()
        else:
            print("master no action required")
            return

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
            self.KillSwitch("isSignal: invalid analysis")

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

    def KillSwitch(self, reason):
        print(reason)
        if self.currentTrade is not None:
            self.currentTrade.close()
        sys.exit(0)

    def sleepTillNextMinute(self, overflow=1, prin=False):
        if prin:
            print("sleeping till next minute")
        sleeptime = 60 - datetime.datetime.utcnow().second
        time.sleep(sleeptime + 1)

    def main(self):
        # self.sleepTillNextMinute(prin=True)
        self.lookForTrades()


if __name__ == '__main__':
    scan = Scan("SPY")
    scan.main()
