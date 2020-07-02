import alpaca_trade_api
import time
import threading


class Trade(threading.Thread):
    def __init__(self, scanObject, api: alpaca_trade_api.REST, bias):
        super().__init__()
        self.master = scanObject
        self.side = "buy" if self.master.bias == "bull" else "sell"
        self.bias = bias
        self.type = type
        self.filled = True
        self.PL = 0
        self.master.openTrade = True
        self.api = api
        self.order = None
        self.stopSignal = threading.Event()
        self.condition = threading.Condition(threading.Lock())

    def open(self):
        # market orders for now.
        self.order = self.api.submit_order(symbol=self.master.symbol, qty=1, side=self.side, type="market", time_in_force="day")

    def close(self):
        self.api.close_all_positions()

    def run(self):
        while not self.stopSignal.isSet():
            self.order = self.api.get_order(self.order.order_id)
            print(self.order)

