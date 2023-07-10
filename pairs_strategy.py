from backtesting import Strategy, Backtest
import pandas as pd
import yfinance as yf
import statsmodels.api as sm

def getData(stock, period="2y", interval="1d"):
    data = yf.download(stock, period=period, interval=interval)
    data = data[['Open', 'High', 'Low', 'Close', 'Volume']] 
    return data

def zscore(series):
    return (series - series.mean()) / series.std()

def hedge_ratio(stockData1, stockData2):
    X = stockData1["Close"]
    y = list(stockData2["Close"])
    X = sm.add_constant(X)
    print(f"Dimensions of matrix in hedge ratio calc: X: {X.shape}, y: {len(y)}")
    model = sm.OLS(y, X)
    results = model.fit()
    ratio = results.params[1]
    ratio = max(0, ratio)
    ratio = min(1, ratio)
    return ratio

def spread(stockData1, stockData2):
    X = stockData1["Close"]
    y = list(stockData2["Close"])
    X = sm.add_constant(X)
    print(f"Dimensions of matrix in spread calc: X: {X.shape}, y: {len(y)}")

    model = sm.OLS(y, X)
    results = model.fit()
    spread = results.resid

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
        self.spread = self.I(spread, stock1Data, stock2Data)
        self.position_entered = False


    def next(self):
        if self.spread > 1.5:
        # Short AAPL, long MSFT
            # print(f"SL: {self.stop_loss}, TP: {self.take_profit}")
            self.buy(size=self.get_size(), sl=self.long_sl(), tp=self.long_tp())  # Enter the position
            self.position_entered = True
        elif self.spread < -1.5:
            self.sell(size=self.get_size(), sl=self.short_sl(), tp=self.short_tp())  # Enter the position
            self.position_entered = True
        # elif self.position_entered and abs(self.spread) < 0.1:  # Exit the position when spread settles at 0
        #     self.position_entered = False
        #     self.position.close()

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
        self.hedge_ratio = hedge_ratio(stock1Data, stock2Data)

        # self.spread = self.I(spread, stock1Data, stock2Data)
        self.position_entered = False
    def next(self):
        if self.spread > 1.5:
            # print(f"SL: {self.stop_loss}, TP: {self.take_profit}")
            self.sell(size=self.get_size(), sl=self.short_sl(), tp=self.short_tp())  # Enter the position
            self.position_entered = True
        elif self.spread < -1.5:
            # print(f"SL: {self.stop_loss}, TP: {self.take_profit}")
            self.buy(size=self.get_size(), sl=self.long_sl(), tp=self.long_tp())  # Enter the position
            self.position_entered = True
        # elif self.position_entered and abs(self.spread) < 0.1:  # Exit the position when spread settles at 0
        #     self.position_entered = False
        #     self.position.close()

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

# # Optimization loop
# best_results_aapl = {"6mo": None, "1y": None, "2y": None, "5y": None}
# best_results_msft = {"6mo": None, "1y": None, "2y": None, "5y": None}
# best_params_aapl = {"6mo": None, "1y": None, "2y": None, "5y": None}
# best_params_msft = {"6mo": None, "1y": None, "2y": None, "5y": None}
# period_list = ["6mo", "1y", "2y", "5y"]
# for interval in ("1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"):
#     for period in period_list:
#         try:
#             data_aapl, data_msft = getData(["AAPL", "MSFT"], period, interval)
#             bt_aapl = Backtest(data_aapl, Stock1Strategy, cash=100000, commission=0.002)
#             results_aapl = bt_aapl.run(interval=interval, period=period)
#             if best_results_aapl[period] is None or (bt_aapl and results_aapl["Equity Final [$]"] > best_results_aapl[period]["Equity Final [$]"]):
#                 best_results_aapl[period] = [results_aapl, bt_aapl]
#                 best_params_aapl[period] = interval
#         except:
#             continue
#         try:
#             data_aapl, data_msft = getData(["AAPL", "MSFT"], period, interval)
#             bt_msft = Backtest(data_msft, Stock2Strategy, cash=100000, commission=0.002)
#             results_msft = bt_msft.run(interval=interval, period=period) 
#             if best_results_msft[period] is None or (bt_msft and results_msft["Equity Final [$]"] > best_params_msft[period]["Equity Final [$]"]):
#                 best_results_msft[period] = [results_msft, bt_msft]
#                 best_params_msft[period] = interval
#         except:
#             continue

# for period in period_list:
#     print(f"----------Results for {period} period----------")
#     print(f"AAPL Best Interval: {best_params_aapl[period]}")
#     print(f"MSFT Best Interval:  {best_params_msft[period]}")

#     print("\n\n")
#     print("----AAPL Backtest----\n", best_results_aapl[period][0], "\n\n")
#     print("----MSFT Backtest----\n", best_results_msft[period][0])
#     print("\n\n")
#     data_aapl, data_msft = getData(["AAPL", "MSFT"], period, interval)
#     bt_aapl = best_results_aapl[period][1]
#     bt_aapl.plot()

#     bt_msft = best_results_msft[period][1]
#     bt_msft.plot()

def backtest_pairs(stock1, stock2):
    period, interval =  "1y", "60m"
    stock1Data = getData(stock1, period, interval)
    stock2Data = getData(stock2, period, interval)
    bt_stock1 = Backtest(stock1Data, Stock1Strategy, cash=100000, commission=0.002)
    results_stock1 = bt_stock1.run(interval=interval, period=period, stock2=stock2, stock1=stock1)
    bt_stock1.plot()
    bt_stock2 = Backtest(stock2Data, Stock2Strategy, cash=100000, commission=0.002)
    results_stock2 = bt_stock2.run(interval=interval, period=period, stock1=stock1, stock2=stock2) 
    bt_stock2.plot()

    

    print(f"{stock1} results: \n\n{results_stock1}\n\n {stock2} results: \n\n{results_stock2}")
    
    return results_stock1, results_stock2
# aapl_opt = bt_aapl.optimize(stop_loss = range(1, 10, 1), 

#                             take_profit = range(10, 101, 5), 
#                             maximize="Equity Final [$]")

# msft_opt = bt_msft.optimize(stop_loss = range(1, 10, 1), 
#                             take_profit = range(10, 101, 5), 
#                             maximize="Equity Final [$]")

# print(f"AAPL results: \n{aapl_opt['_strategy']}\n", aapl_opt)
# print(f"MSFT results: \n {msft_opt['_strategy']}\n", msft_opt)