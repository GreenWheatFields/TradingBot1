class Trade:
    def __init__(self, bias, scanObject, type, api):
        self.master = scanObject
        self.type = type
        self.bias = bias
        self.filled = True
        self.PL = 0
        self.master.openTrade = True
        self.api = api
    def open(self):
        print(self.master.symbol)
        print(self.api.get_barset(symbols="SPY", limit=1, timeframe="minute")["SPY"][0])
        pass
    def close(self):
        pass

    def log(self):
        pass


