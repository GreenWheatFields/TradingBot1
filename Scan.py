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
        self.alpacaAPI = alpaca_trade_api.REST(ALPACA_PUBLIC_KEY, ALPACA_PRIVATE_KEY, api_version="v2")
        self.currentTime = datetime.datetime.now()
        self.testingTime = datetime.datetime(2020, 6, 26, 13, 49)
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
        barSize = self.latestCandle.o - self.latestCandle.c
        minimumReq = barSize * 0.501
        self.SMA = sum(self.lastXClosingPrices) / len(self.lastXClosingPrices)
        smaHeight = self.SMA - self.latestCandle.c
        outsideSMA = False
        insideSMA = True
        above = below = None

        if barSize <= 0:
            barSize = toPositive(barSize)
            minimumReq = toPositive(barSize)
        if smaHeight < 0:
            smaHeight = toPositive(smaHeight)
        if smaHeight > barSize or smaHeight < 0:
            print("out of bounds")
            outsideSMA = True
            insideSMA = not outsideSMA
            above = smaHeight < 0
            below = not above

        viableCrossover = smaHeight > minimumReq and insideSMA




    def onTick(self):
        # once awake, check prices, get new SMA, check for a signal
        self.lastXClosingPrices = self.getClosingPrices(10)
        print(self.lastXClosingPrices)
        self.latestCandle = Scan.alpacaAPI.get_barset(symbols=self.symbol, limit=1, end="{}-04:00".format(self.testingTime.strftime(Scan.alpacaDateTimeFormat)), timeframe="minute")[self.symbol][0]
        self.lastXClosingPrices.pop(0)
        self.lastXClosingPrices.append(self.latestCandle.c)
        self.candleColor = "green" if self.latestCandle.o < self.latestCandle.c else "red"
        if self.isSignal():
            # do something
            pass
        else:
            # do somethings else, proably sleep
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
