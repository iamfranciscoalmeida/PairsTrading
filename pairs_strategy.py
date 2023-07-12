from backtesting import Strategy, Backtest
import pandas as pd
import yfinance as yf
import statsmodels.api as sm
import numpy as np
from utils import *

def hedge_ratio(stockData1, stockData2):
    X = stockData1["Close"]
    y = list(stockData2["Close"])
    X = sm.add_constant(X)
    model = sm.OLS(y, X)
    results = model.fit()
    ratio = results.params[1]
    ratio = max(0.01, ratio)
    ratio = min(1, ratio)
    return ratio

def spread(stockData1, stockData2, dataLen):
    X = stockData1["Close"]
    y = list(stockData2["Close"])
    X = sm.add_constant(X)
    
    model = sm.OLS(y, X)
    results = model.fit()
    spread = results.resid
    # spread = y - X * results.params[1] - results.params[0]
    spread_length = len(spread)
    if spread_length < dataLen:
        spread = np.append(spread, [np.nan] * (dataLen - spread_length))

    return zscore(spread)

class Stock1Strategy(Strategy):
    period, interval =  "1y", "60m"
    stop_loss = 5
    take_profit = 15
    stock1 = None
    stock2 = None
    def init(self):
        stock2Data = getData(self.stock2, self.period, self.interval)
        stock1Data = getData(self.stock1, self.period, self.interval)
        stock1Data, stock2Data = stock1Data.align(stock2Data, join='inner')
        self.hedge_ratio = hedge_ratio(stock1Data, stock2Data)
        self.spread = self.I(spread, stock1Data, stock2Data, len(self.data.Close))
        self.position_entered = False


    def next(self):
        if self.spread > 1.5:
            self.buy(size=self.get_size(), sl=self.long_sl(), tp=self.long_tp())  # Enter the position
        elif self.spread < -1.5:
            self.sell(size=self.get_size(), sl=self.short_sl(), tp=self.short_tp())  # Enter the position

    def short_sl(self):
        return self.data["Close"] * (1 + self.stop_loss / 100)
    
    def long_sl(self):
        return self.data["Close"] * (1 - self.stop_loss / 100)   
    
    def short_tp(self):
        return self.data["Close"] * (1 - self.take_profit / 100)
    
    def long_tp(self):
        return self.data["Close"] * (1 + self.take_profit / 100)
    
    def get_size(self):
        size = 100 / (self.data.Close[-1] * (1 + self.hedge_ratio))
        size = min(.99, size)
        return size 

class Stock2Strategy(Strategy):
    period, interval =  "1y", "60m"   
    stop_loss = 5
    take_profit = 15
    stock1 = None
    stock2 = None
    def init(self):
        stock1Data = getData(self.stock1, self.period, self.interval)
        # stock1, stock2 = stock1.align(stock2, join='inner')
        stock2Data = getData(self.stock2, self.period, self.interval)
        stock1Data, stock2Data = stock1Data.align(stock2Data, join='inner')
        self.spread = self.I(spread, stock1Data, stock2Data, len(self.data.Close))
        self.hedge_ratio = hedge_ratio(stock1Data, stock2Data)

    def next(self):
        if self.spread > 1.5:
            self.sell(size=self.get_size(), sl=self.short_sl(), tp=self.short_tp())  # Enter the position
        elif self.spread < -1.5:
            self.buy(size=self.get_size(), sl=self.long_sl(), tp=self.long_tp())  # Enter the position

    def short_sl(self):
        return self.data["Close"] * (1 + self.stop_loss / 100)
    
    def long_sl(self):
        return self.data["Close"] * (1 - self.stop_loss / 100)   
    
    def short_tp(self):
        return self.data["Close"] * (1 - self.take_profit / 100)
    
    def long_tp(self):
        return self.data["Close"] * (1 + self.take_profit / 100)
    
    def get_size(self):
        size = self.hedge_ratio * 100 / (self.data.Close[-1] * (1 + self.hedge_ratio))
        size = min(.99, size)
        return size
    
# def opt(bt_stock1: Backtest, bt_stock2: Backtest):
#     bt1_opt = bt_stock1.optimize(stop_loss=range(1, 4, 1),
#                                  take_profit=range(10,13,2), 
#                                  maximize="Equity Final [$]")
#     bt2_opt = bt_stock2.optimize(stop_loss=range(1, 2, 1),
#                                  take_profit=range(10,13,2), 
#                                  maximize="Equity Final [$]")
#     print(bt1_opt)
    
    
def backtest_pairs(stock1, stock2, period="1y", interval="60m"):
    stock1Data = getData(stock1, period, interval)
    stock2Data = getData(stock2, period, interval)
    
    bt_stock1 = Backtest(
        stock1Data, Stock1Strategy, cash=100000, commission=0.002
    )
    results_stock1 = bt_stock1.run(
        interval=interval, period=period, stock2=stock2, stock1=stock1
    )
    
    bt_stock2 = Backtest(
        stock2Data, Stock2Strategy, cash=100000, commission=0.002
    )
    results_stock2 = bt_stock2.run(
        interval=interval, period=period, stock1=stock1, stock2=stock2
    )
     
    return results_stock1, results_stock2
