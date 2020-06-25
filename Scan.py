import time

import alpaca_trade_api
from KEYS import *
import datetime
import pprint
import json
import sys
import requests


class Scan:
    def __init__(self, symbol):
        self.symbol = symbol
        self.alpacaAPI = alpaca_trade_api.REST(ALPACA_PUBLIC_KEY, ALPACA_PRIVATE_KEY, api_version="v2")
        self.currentTime = datetime.datetime.now()
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

            self.lastXClosingPrices = self.getClosingPrices(10)
            print(self.lastXClosingPrices)
            sys.exit(0)
            #self.candleColor = "red" if self.lastXCandles.o > self.lastXCandles.c else "green"
            self.isSignal()
        else:
            self.checkMarketConditions()

    def isSignal(self):
        barSize = self.latestCandle.o - self.latestCandle.c
        minimumReq = barSize * 0.501
        smaHeight = self.SMA - self.latestCandle.c
        outsideSMA = False
        insideSMA = False

        if self.candleColor == "green":
            # convery negative values to positive
            barSize = barSize * -1
            smaHeight = smaHeight * -1
            minimumReq = minimumReq * -1
        if barSize < 0 or smaHeight < 0 or minimumReq < 0:
            pass

        if smaHeight > barSize or smaHeight < 0:
            print("out of bounds")
            outsideSMA = True
        else:
            print("candle inside SMA")
            insideSMA = True

        viableCrossover = smaHeight > minimumReq and insideSMA

        if viableCrossover:
            print("viable crossover")
        else:
            print("non viable corssover")

    def onTick(self):
        #once awake, check prices, get new SMA, check for a signal
        self.latestCandle = self.alpacaAPI.get_barset(symbols=self.symbol, limit=1, end="2020-06-24T9:29:00-04:00",timeframe="minute")[self.symbol]
        if self.isSignal():
            #do something
            pass
        else:
            # do somethings else, proably sleep
            pass

    def checkMarketConditions(self):
        response = self.alpacaAPI.get_clock()
        self.isMarketOpen = response.is_open
        self.nextOpen = response.next_open
        self.nextClose = response.next_close

    def getClosingPrices(self, amount: int) -> list:
        #eventually should include premarket data, for now just going to call this method at 9:41
        #return [i.c for i in self.alpacaAPI.get_barset(symbols=self.symbol, limit=amount, end="2020-06-24T9:29:00-04:00",timeframe="minute")[self.symbol]]
        # testing iex extended
        # do at 9:20
        closing = []
        #time.sleep(sleeptime)
        while len(closing) < 10:
            x = requests.get("https://cloud.iexapis.com/v1/stock/{}/quote?token={}".format(self.symbol,IEX_PRIVATE_KEY))
            closing.append(x["extendedPrice"])
            t = datetime.datetime.utcnow()
            sleeptime = 60 - (t.second + t.microsecond / 1000000.0)
            time.sleep(sleeptime)
            # sub second precision, but it may be too fast for the api to update, hopefully not
        return closing

    @staticmethod
    def KillSwitch(self):
        pass


class Monitor:
    def __init__(self):
        pass

    #   take in a trade object as a parameter

    def isJusted(self):
        pass

    def printStats(self):
        pass

    def monitor(self):
        pass


if __name__ == '__main__':
    # scan/ lookfortrades() could take in a symbol as a parameter, for now, spy
    scan = Scan("SPY")
    scan.lookForTrades()
