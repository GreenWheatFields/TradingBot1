import alpaca_trade_api
from KEYS import *
import datetime
import pprint


class Scan:
    def __init__(self):
        self.alpacaAPI = alpaca_trade_api.REST(ALPACA_PUBLIC_KEY, ALPACA_PRIVATE_KEY, api_version="v2")
        self.currentTime = datetime.datetime.now()
        self.isMarketOpen = True
        self.nextOpen = None
        self.nextClose = None
        self.SMA = None
        self.minuteBar = None
        self.openTrade = False
    def lookForTrades(self):
        # technical indicators from alpha vantage are off until around 9:44/ my own calculations are off so we'll have to wait until 9:44 before trading
        if self.isMarketOpen:
            # while self.currentTime.second != 0:
            #     print("waitng")
            #     print(self.currentTime)
            #     self.currentTime = datetime.datetime.now()
            self.minuteBar = self.alpacaAPI.get_barset(symbols="SPY", limit=1, end="2020-06-19T13:00:00-04:00", timeframe="minute")["SPY"][0]
            self.SMA = self.alpacaAPI.alpha_vantage.techindicators(symbol="SPY", interval="1min", time_period=10, series_type="close")
            self.SMA = float(self.SMA['Technical Analysis: SMA']["2020-06-19 13:00"]["SMA"])
            print(self.SMA)
            self.isSignal()

        self.checkMarketConditions()
        #print(type(self.nextClose))

    def KillSwitch(self):
        pass

    def checkMarketConditions(self):
        response = self.alpacaAPI.get_clock()
        self.isMarketOpen = response.is_open
        # TODO see if i need to parse time further
        self.nextOpen = response.next_open
        self.nextClose = response.next_close

    def isSignal(self):
        signal = self.minuteBar.o - self.minuteBar.c
        if self.minuteBar.c > self.SMA and not self.openTrade:
            #perhaps return a signal object
            print("here!")
            # will need to check if their is an open position, and the direction of that position before signally anything
            return False


if __name__ == '__main__':
    scan = Scan()
    scan.lookForTrades()
