import pandas as pd
from statsmodels.tsa.stattools import coint
import yfinance as yf

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

def is_cointegrated(stock1, stock2):
    """Checks if two stocks are cointegrated and have a positive correlation"""
    stockData1 = yf.download(stock1, period="2y", interval="60m")["Close"]
    stockData2 = yf.download(stock2, period="2y", interval="60m")["Close"]
    stockData1, stockData2 = stockData1.align(stockData2, join='inner')

    score, pvalue, _ = coint(stockData1, stockData2)
    cor = stockData1.corr(stockData2)
    return True if pvalue < 0.05 and cor > 0.5 else False


def find_cointegrated_stocks(stockList):
    added_stocks = set()
    coint_stocks = {}
    for stock1 in stockList:
        for stock2 in stockList:
            if stock1 == stock2: continue
            if is_cointegrated(stock1, stock2):
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