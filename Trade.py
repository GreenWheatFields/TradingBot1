import alpaca_trade_api
import time
import threading


class Trade(threading.Thread):
    def __init__(self, scanObject, api: alpaca_trade_api.REST, bias):
        # self.close_all_positions is a massive bottleneck that will make it impossible to scan
        super().__init__()
        self.master = scanObject
        self.side = "buy" if self.master.bias == "bull" else "sell"
        self.priceType = "askprice" if self.side == "sell" else "bidprice"
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
        print("trade object opening order")
        self.order = self.api.submit_order(symbol=self.master.symbol, qty=1, side=self.side, type="market", time_in_force="day")
        print("trade object waiting for fill")
        time.sleep(2)
        self.order = self.api.get_order(self.order.id)
        if self.order.filled_avg_price is None:
            # todo, handle this exception better
            time.sleep(2)
        else:
            print(self.order)
        return

    def close(self):
        self.api.close_all_positions()
        self.master.currentTrade = None

    def run(self):
        self.openAndMonitor()
        self.trailingStop = float(self.order.filled_avg_price) - self.lossTooBig
        while not self.stopSignal.isSet():
            self.currentPrice = float(getattr(self.api.get_last_quote(self.master.symbol), self.priceType))
            print(self.currentPrice, "current stock price")
            print(self.trailingStop, "trade trailing stop")
            if self.currentPrice < self.trailingStop:
                print("trailing stop hit")
                print(self.currentPrice, "current price", self.trailingStop, "trailing stop")
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
