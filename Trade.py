import alpaca_trade_api
import time


class Trade:
    def __init__(self, scanObject, type, api: alpaca_trade_api.REST, bias):
        self.master = scanObject
        self.side = "buy" if self.master.bias == "bull" else "sell"
        self.bias = bias
        self.type = type
        self.filled = True
        self.PL = 0
        self.master.openTrade = True
        self.api = api
        self.order = None

    def open(self):
        # market orders for now.
        stopLoss = self.master.latestCandle.c - .20 if self.master.bias == "bull" else self.master.latestCandle.c + .20
        self.order = self.api.submit_order(symbol=self.master.symbol, qty=1, type="market", time_in_force="gtc", side=self.side, take_profit={"limit_price": 500},
                                      stop_loss={"stop_price": stopLoss, "limit_price": stopLoss - 1})
        self.order = self.api.get_order(self.order.id)

    def close(self):
        self.api.close_all_positions()

    def log(self):
        pass
