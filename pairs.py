""""Goal: to input a list of stocks, find two stocks that correlate, and find the point at which to execute a trade: 
        - short 
        - long
"""
import yfinance as yf
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import pearsonr
import seaborn as snb
import numpy as np
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint, adfuller
from cointegration import *
from backtesting import Strategy, Backtest
from pairs_strategy import *
import time


def correlation(stock1, stock2):
    data = pd.DataFrame(yf.download([stock1, stock2], period="1y", interval="60m")['Close'])
    return data[stock1].corr(data[stock2])

def corr_heatmap(corr_matrix):
    # Generate a mask for the upper triangle
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))

    # Set up the matplotlib figure
    f, ax = plt.subplots(figsize=(11, 9))

    # Generate a custom diverging colormap
    cmap = snb.diverging_palette(230, 20, as_cmap=True)

    # Draw the heatmap with the mask and correct aspect ratio
    snb.heatmap(corr_matrix, mask=mask, cmap=cmap, center=0, annot=True,
            square=True, linewidths=.5, cbar_kws={"shrink": .5})

    plt.show()

def corr_matrix(stocks_data):
    matrix = stocks_data.corr()
    # corr_heatmap(matrix)
    return matrix

def hypothesis_test(stock1_data, stock2_data):
    """"
    Null: no correlation
    Alternative: there is a correlation
    """
    corr, pvalue = pearsonr(stock1_data, stock2_data)
    print("corr, pvalue: ", corr, pvalue)
    return True if pvalue < 0.01 else False

def plot_diff(data, stock1, stock2):
    plt.figure(figsize=(14, 7))
    plt.plot(data[stock1] - data[stock2], label="Diference")
    plt.plot(data[stock2], label=stock2)
    plt.title(f"Historical price difference between {stock1} and {stock2}")
    plt.xlabel("Date")
    plt.ylabel("Closing Price")
    plt.legend()
    plt.show()

def plot(data, stock1, stock2):
    plt.figure(figsize=(14, 7))
    plt.plot(data[stock1], label=stock1)
    plt.plot(data[stock2], label=stock2)
    plt.title(f"Historical price data between {stock1} and {stock2}")
    plt.xlabel("Date")
    plt.ylabel("Closing Price")
    plt.legend()
    plt.show()

def zscore(series):
    return (series - series.mean()) / series.std()

def spread(stock1, stock2):

    # Drop any missing data for accuracy

    X = getData(stock1, period="1y", interval="60m")["Close"]
    y = getData(stock2, period="1y", interval="60m")["Close"]
    X = sm.add_constant(X)

    # Perform the regression
    model = sm.OLS(y, X)
    results = model.fit()
    print("summary of regression\n", results.summary())
    spread = results.resid
    hedge_ratio = results.params["Close"]
    # S1 = data[stock1]
    # S2 = data[stock2]
    # S1 = sm.add_constant(S1)

    # results = sm.OLS(S2, S1).fit()

    # b = results.params[stock1]
    # print("b", b)
    # spread = S2 - b * S1
    # spread = X/y
    spread_standardized = (spread - spread.mean()) / spread.std()
    # spread_standardized.plot()
    # Plot the spread
    plt.figure(figsize=(12,7))
    plt.plot(spread_standardized, label='Spread')
    plt.plot(zscore(X), label=f"{stock1} price")
    plt.plot(zscore(y), label=f"{stock2} price")
    # plt.axhline(spread_standardized.mean(), color='black')
    plt.axhline(1, color='green', linestyle='dotted', label='Short entry')
    plt.axhline(-1, color='red', linestyle='dotted', label='Long entry')

    # If < -1, short stock 1 long stock2
    # if > 1, short stock 2 long stock 1

    plt.legend()
    plt.show()

def pairs(stocks, start_date, end_date):

    checked_stocks = set()
    correlating_stocks = set()
    all_data = yf.download(stocks, period="6mo", interval="1h")['Close']
    matrix = corr_matrix(all_data)
    correlated = matrix > 0.8
    print(correlated)
    # print(corr_matrix(all_data))
    
    spread(all_data, "AAPL", "MSFT")
    score, pvalue, _ = coint(all_data["AAPL"], all_data["GOOG"])
    print("AAPL, GOOG COINT", pvalue)

    return []

def calculate_portfolio_sharpe(returns, volatilities, risk_free_rate = 3):
    weight = 1 / len(returns)
    weight_array = [weight] * len(returns)
    portfolio_ret = np.dot(returns, weight_array)
    portfolio_sd = np.sqrt(np.dot(np.square(volatilities), np.square(weight_array)))
    return (portfolio_ret - risk_free_rate) / portfolio_sd
    
def write_results_to_file(resultsDict: dict, risk_free_rate = 3):
    path = "results.txt"
    cumulative_ret = 0
    vol_array = []
    ret_array = []
    with open(path, "w") as f:
        for pair, results in resultsDict.items():
            stock1Results = results[0]
            stock2Results = results[1]
            vol_array.append(stock1Results["Volatility (Ann.) [%]"])
            vol_array.append(stock2Results["Volatility (Ann.) [%]"])
            cumulative_ret += (stock1Results["Return [%]"] + stock2Results["Return [%]"]) 
            ret_array.append(stock1Results["Return [%]"])
            ret_array.append(stock2Results["Return [%]"])            
            stock1, stock2 = pair.split("-")[0], pair.split("-")[1]
            f.write(f"Pair: {pair} \n\n{stock1}:\n\n{stock1Results}\n\n{stock2}:\n\n{stock2Results}\n\n\n\n")
        cumulative_ret *= len(ret_array)
        sharpe = calculate_portfolio_sharpe(ret_array, vol_array, risk_free_rate)
        weights = [1/len(ret_array)] * len(ret_array)
        portfolio_ret = np.dot(ret_array, weights)
        f.write(f"Cumulative return ($): ${cumulative_ret}\n% return: {portfolio_ret}\nPortfolio sharpe ratio: {sharpe}\n")

if __name__ == "__main__":
    start_time = time.time()
    # stocks = read_sp500_tickers("newtickers.csv")
    # cointegrated_stocks = find_cointegrated_stocks(stocks)
    cointegrated_stocks = {'GOOG': ['AAPL'], 'AXP': ['TSM'], 'ACN': ['GOOG'], 'VICI': ['VTR'], 'VZ': ['TMUS', 'PARA'], 'TMUS': ['T', 'PARA'], 'BBWI': ['BBY', 'HD'], 'CNC': ['DHR'], 'CRL': ['CI'], 'CVS': ['DHR'], 'HOLX': ['IDXX'], 'ILMN': ['BMY', 'CI', 'CNC', 'COO', 'CRL', 'CTLT', 'CVS', 'DGX', 'DHR', 'GILD', 'HCA', 'HOLX', 'HUM', 'IDXX']}
    print(cointegrated_stocks)
    results = {}
    for key, value in cointegrated_stocks.items():
        stock1 = key
        for stock2 in value:
            print(f"Correlation between {stock1} and {stock2}: {correlation(stock1, stock2)}")
            results1, results2 = backtest_pairs(stock1, stock2)
            results_key = f"{stock1}-{stock2}"
            results[results_key] = [results1, results2]
            
    write_results_to_file(results)
    end_time = time.time()
    time_taken = round(end_time - start_time, 2)
    print(f"--------Time taken {time_taken}s--------")