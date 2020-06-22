import alpaca_trade_api
from KEYS import *
import datetime
import pprint
import json


class Scan:
    def __init__(self, symbol):
        self.symbol = symbol
        self.alpacaAPI = alpaca_trade_api.REST(ALPACA_PUBLIC_KEY, ALPACA_PRIVATE_KEY, api_version="v2")
        self.currentTime = datetime.datetime.now()
        self.isMarketOpen = True
        self.nextOpen = None
        self.nextClose = None
        self.SMA = None
        self.minuteBar = None
        self.openTrade = False
        self.barColor = None

    def lookForTrades(self):
        if self.isMarketOpen:
            # while self.currentTime.second != 0:
            #     print("waitng")
            #     print(self.currentTime)
            #     self.currentTime = datetime.datetime.now()
            self.minuteBar = \
            self.alpacaAPI.get_barset(symbols=self.symbol, limit=1, end="2020-06-19T11:54:00-04:00", timeframe="minute")[
                self.symbol][0]
            self.barColor = "red" if self.minuteBar.o > self.minuteBar.c else "green"
            self.SMAlist = self.alpacaAPI.alpha_vantage.techindicators(symbol=self.symbol, interval="1min", time_period=10,
                                                                   series_type="close")
            self.SMA = float(self.SMAlist['Technical Analysis: SMA']["2020-06-19 11:55"]["SMA"])
            self.isSignal()
        else:
            self.checkMarketConditions()

    def checkMarketConditions(self):
        response = self.alpacaAPI.get_clock()
        self.isMarketOpen = response.is_open
        self.nextOpen = response.next_open
        self.nextClose = response.next_close

    def isSignal(self):
        print(self.minuteBar)
        print(self.barColor)
        barSize = self.minuteBar.o - self.minuteBar.c
        minimumReq = barSize * 0.501
        smaHeight = self.SMA - self.minuteBar.c
        outsideSMA = False
        insideSMA = False

        if self.barColor == "green":
            #convery negative values to positive
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
