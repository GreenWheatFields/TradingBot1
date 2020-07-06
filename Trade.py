import alpaca_trade_api
import time
import threading


class Trade(threading.Thread):
    def __init__(self, scanObject, api: alpaca_trade_api.REST, bias):
        # self.close_all_positions is a massive bottleneck that will make it impossible to scan
        super().__init__()
        self.master = scanObject
        self.side = "buy" if self.master.bias == "bull" else "sell"
        self.bias = bias
        self.api = api
        self.order = None
        self.stopSignal = threading.Event()
        self.sleepLock = threading.Condition(threading.Lock())
        self.lossTooBig = -.50
        self.trailingStop = None
        self.trailingStopLast = 0
        self.currentPrice = 0

    def openAndMonitor(self):
        # market orders for now.
        self.order = self.api.submit_order(symbol=self.master.symbol, qty=1, side=self.side, type="market", time_in_force="day")
        self.order = self.api.get_order(self.order.id)
        self.start()

    def close(self):
        self.api.close_all_positions()
        self.master.currentTrade = None

    def run(self):
        self.trailingStop = self.order.filled_avg_price - self.lossTooBig
        while not self.stopSignal.isSet():
            self.currentPrice = self.api.get_last_quote(self.master.symbol)
            if float(self.currentPrice) < self.trailingStop:
                print("closing due to intial stop price hit")
                self.close()
                break
            else:
                self.trailingStop = self.currentPrice - .50
                with self.sleepLock:
                    self.sleepLock.wait(.75)

    def interrupt(self):
        with self.sleepLock:
            self.sleepLock.notify()
        self.stopSignal.set()
