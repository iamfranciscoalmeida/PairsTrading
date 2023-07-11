""""Goal: to input a list of stocks, find two stocks that correlate, and find the point at which to execute a trade: 
        - short 
        - long
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from cointegration import *
from pairs_strategy import *
import time
    
def calculate_portfio_returns(returns):
    weights = [1/len(returns)] * len(returns)
    portfolio_ret = np.dot(returns, weights)
    return portfolio_ret
def change_column_names(df):
    new_column_names = []
    for i, column in enumerate(df.columns):
        new_name = f"{column} {i+1}"
        new_column_names.append(new_name)
    df.columns = new_column_names
    return df

def calculate_portfolio_sharpe(returns, volatilities, risk_free_rate = 3):
    weight = 1 / len(returns)
    weight_array = [weight] * len(returns)
    portfolio_ret = np.dot(returns, weight_array)
    portfolio_sd = np.sqrt(np.dot(np.square(volatilities), np.square(weight_array)))
    return (portfolio_ret - risk_free_rate) / portfolio_sd

def max_drawdown(cumulative_returns):
    # Calculate the running maximum
    running_max = np.maximum.accumulate(cumulative_returns)
    running_max[running_max < 1] = 1
    
    # Calculate the drawdown
    drawdown = cumulative_returns / running_max - 1
    
    # Return the minimum drawdown (i.e., maximum drawdown)
    return drawdown.min()

def plot_total_portfolio_ret(equity_curves, sharpe):
    equity_only_curves = [curve["Equity"] for curve in equity_curves]
    cumulative_equity_curve = pd.concat(equity_only_curves, axis=1)
    aligned_equity_curve = cumulative_equity_curve.resample('D').last().ffill()
    pct_returns = pd.DataFrame()
    new_equity_curve = change_column_names(aligned_equity_curve)
    for column in new_equity_curve.columns:
        if pd.isna(new_equity_curve[column].iloc[0]):
            new_equity_curve[column].iloc[0] = 100000
            pct_return = ((new_equity_curve[column] / new_equity_curve[column].iloc[0]) - 1) * 100
        else:
            pct_return = ((new_equity_curve[column] / new_equity_curve[column].iloc[0]) - 1) * 100
        pct_returns[column] = pct_return
    cumulative_pct_returns = pct_returns.sum(axis=1) / len(new_equity_curve.columns)
    max_draw = max_drawdown(cumulative_pct_returns)
    spy = getData("SPY", period="1y", interval="1d")["Close"]
    spy_daily_returns = spy.pct_change()
    spy_cum_daily_returns = (1 + spy_daily_returns).cumprod() - 1
    spy_cum_daily_returns.index = pd.to_datetime(spy_cum_daily_returns.index)  # Convert index to DatetimeIndex
    spy_cum_returns = spy_cum_daily_returns * 100
    plt.plot(cumulative_pct_returns, color="blue", label="Portfolio Returns (%)")
    plt.plot([], [], ' ', label=f"Por. Max Drawdown: {max_draw:.2f}")
    plt.plot([], [], ' ', label=f"Sharpe Ratio: {sharpe:.2f}")
    plt.plot(spy_cum_returns, color="red", label="SPY Returns (%)")
    plt.title('Pairs Trading Portfolio Equity', fontsize=14, color='black')
    plt.xlabel('Time', fontsize=12)
    plt.ylabel('Percentage Return', fontsize=12)
    plt.legend()
    plt.show()

def write_results_to_file(resultsDict: dict, risk_free_rate = 3):
    path = "results.txt"
    cumulative_ret = 0
    vol_array = []
    ret_array = []
    equity_curves_array = []
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
            equity_curves_array.append(stock1Results['_equity_curve'])
            equity_curves_array.append(stock2Results['_equity_curve'])
            f.write(f"Pair: {pair} \n\n{stock1}:\n\n{stock1Results}\n\n{stock2}:\n\n{stock2Results}\n\n\n\n")
        cumulative_ret *= len(ret_array)
        sharpe = calculate_portfolio_sharpe(ret_array, vol_array, risk_free_rate)
        portfolio_ret = calculate_portfio_returns(ret_array)
        plot_total_portfolio_ret(equity_curves_array, sharpe)
        f.write(f"Cumulative return ($): ${cumulative_ret}\n% return: {portfolio_ret}\nPortfolio sharpe ratio: {sharpe}\n")


if __name__ == "__main__":
    start_time = time.time()
    # stocks = read_sp500_tickers("newtickers.csv")
    # cointegrated_stocks = find_cointegrated_stocks(stocks)
    cointegrated_stocks = {'GOOG': ['AAPL'], 'LINK-USD': ['ADA-USD'],  'AXP': ['TSM'], 'ACN': ['GOOG'], 'VICI': ['VTR'], 'VZ': ['TMUS', 'PARA'], 'TMUS': ['T', 'PARA'], 'BBWI': ['BBY', 'HD'], 'CNC': ['DHR'], 'CVS': ['DHR'], 'HOLX': ['IDXX'], 'ILMN': ['BMY', 'CI', 'CNC', 'COO', 'CRL', 'CTLT', 'CVS', 'DHR', 'GILD', 'HCA', 'HOLX', 'HUM', 'IDXX'], 'DOT-USD': ['VET-USD','XRP-USD', 'XLM-USD', 'VET-USD', 'SOL-USD']}
    results = {}
    for key, value in cointegrated_stocks.items():
        stock1 = key
        for stock2 in value:
            results1, results2 = backtest_pairs(stock1, stock2)
            results_key = f"{stock1}-{stock2}"
            results[results_key] = [results1, results2]
            
    write_results_to_file(results)
    end_time = time.time()
    time_taken = round(end_time - start_time, 2)
    print(f"--------Time taken {time_taken}s--------")