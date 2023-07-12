from matplotlib import pyplot as plt
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint, adfuller
import yfinance as yf

from pairs_strategy import getData, zscore


def correlation(stock1, stock2):
    data = pd.DataFrame(yf.download([stock1, stock2], period="1y", interval="60m")['Close'])
    return data[stock1].corr(data[stock2])

def add_to_dictionary(dict, key, value):
    """add to a dictionary where the value is an array"""
    if key in dict.keys(): 
        dict[key].append(value)
    else:
        dict[key] = [value]
    return dict


def read_sp500_tickers(filename):
    df = pd.read_csv(filename)
    tickers = df['Ticker'].tolist()
    return tickers

def is_cointegrated(stockData1, stockData2):
    """Checks if two stocks are cointegrated and have a positive correlation"""
    stockData1, stockData2 = stockData1["Close"].align(stockData2["Close"], join='inner')

    score, pvalue, _ = coint(stockData1, stockData2)
    cor = stockData1.corr(stockData2)
    return True if pvalue < 0.05 and cor > 0.5 else False


def find_cointegrated_stocks(stockList):
    added_stocks = set()
    coint_stocks = {}
    for stock1 in stockList:
        for stock2 in stockList:
            if stock1 == stock2: continue
            print(stock1, stock2)
            stock1Data = getData(stock1, period="1y", interval="60m")
            stock2Data = getData(stock2, period="1y", interval="60m")
            stock1Data, stock2Data = stock1Data.align(stock2Data, join='inner')  
            if is_cointegrated(stock1Data, stock2Data) and is_stationary(stock1Data, stock2Data):
                if stock1 in added_stocks and stock2 in added_stocks:
                    if stock1 in coint_stocks.keys():
                        if stock2 in coint_stocks[stock1]: continue
                    elif stock2 in coint_stocks.keys():
                        if stock1 in coint_stocks[stock2]: continue

                added_stocks.add(stock2)
                added_stocks.add(stock1)  
                if stock1 in coint_stocks.keys(): coint_stocks[stock1].append(stock2)
                else: coint_stocks[stock1] = [stock2]

    return coint_stocks

def spread_test(stockData1, stockData2):
    X = stockData1["Close"]
    y = list(stockData2["Close"])
    X = sm.add_constant(X)
    
    model = sm.OLS(y, X)
    results = model.fit()
    spread = results.resid
    # spread = y - X * results.params[1] - results.params[0]

    # print(spread)

    return spread

def is_stationary(stockData1, stockData2):
    spr = spread_test(stockData1, stockData2)
    stat, pvalue, *_ = adfuller(spr)
    return True if pvalue < 0.05 else False

if __name__ == "__main__":
#     cointegrated_stocks = {'GOOG': ['AAPL'], 'AXP': ['TSM'], 'ACN': ['GOOG'], 'DOV': ['BA'], 'VICI': ['VTR'], 'VZ': ['TMUS', 'PARA'], 'TMUS': ['T', 'PARA'], 'BBWI': ['BBY', 'HD'], 'CNC': ['DHR'], 'CVS': ['DHR'], 'HOLX': ['IDXX'], 'ILMN': ['BMY', 'CI', 'CNC', 'COO', 'CRL', 'CTLT', 'CVS', 'DHR', 'GILD', 'HCA', 'HOLX', 'HUM', 'IDXX'], 'DOT-USD': ['VET-USD','XRP-USD', 'XLM-USD', 'VET-USD', 'SOL-USD'], 'LINK-USD': ['ADA-USD']}
    # cointegrated_stocks = {'DOT-USD': ['VET-USD','XRP-USD', 'XLM-USD', 'VET-USD', 'SOL-USD'], 'LINK-USD': ['ADA-USD']}
    cointegrated_stocks = {'GOOG': ['AAPL'], 'DOV': ['BA'], 'VICI': ['VTR'], 'VZ': ['PARA'], 'TMUS': ['T'], 'BBWI': ['BBY', 'HD'], 'CNC': ['DHR'], 'CVS': ['DHR'], 'EOG': ['COP'], 'XEL': ['SRE'], 'SRE': ['WEC', 'NEE', 'ES', 'AEP', 'DTE', 'DUK', 'LNT'], 'AEP': ['DUK']}
    newList = {}
    for stock1, value in cointegrated_stocks.items():
        newValue = []
        for stock2 in value: 
            stockData1 = getData(stock1, "1y", "60m")   
            stockData2 = getData(stock2, "1y", "60m")   
            stockData1, stockData2 = stockData1.align(stockData2, join='inner')     
            if is_stationary(stockData1, stockData2) and is_cointegrated(stockData1, stockData2):
                newValue.append(stock2)
        newList[stock1] = newValue 
                
    print(newList)
               
#             # plt.plot(spr)
#             # plt.show()
    