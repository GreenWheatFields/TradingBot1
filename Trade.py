import alpaca_trade_api
import time
import threading


class Trade(threading.Thread):
    def __init__(self, scanObject, api: alpaca_trade_api.REST, bias):
        super().__init__()
        self.master = scanObject
        self.side = "buy" if self.master.bias == "bull" else "sell"
        self.bias = bias
        self.api = api
        self.order = None
        self.monitor = None
        self.stopSignal = threading.Event()
        self.sleepLock = threading.Condition(threading.Lock())
        self.lossTooBig = -.50
        self.trailingStop = None
        self.trailingStopLast = 0

    def openAndMonitor(self):
        # market orders for now.
        self.order = self.api.submit_order(symbol=self.master.symbol, qty=1, side=self.side, type="market", time_in_force="day")
        self.start()
    def close(self):
        self.api.close_all_positions()

    def run(self):
        while not self.stopSignal.isSet():
            self.monitor = self.api.get_position(self.master.symbol)
            print(self.monitor)
            if float(self.monitor.unrealized_pl) < self.lossTooBig:
                print("closing due to intial stop price hit")
                self.api.close_all_positions()
                self.master.currentTrade = None
                break
            elif self.monitor.current_price < self.trailingStop:
                print("trailing stop hit")
                self.api.close_all_positions()
                self.master.currentTrade = None
                break
            else:
                self.trailingStop = self.monitor.current_price - .50
                with self.sleepLock:
                    self.sleepLock.wait(.75)

    def interrupt(self):
        with self.sleepLock:
            self.sleepLock.notify()
        self.stopSignal.set()
