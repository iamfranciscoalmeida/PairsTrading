import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import yfinance
    
def getData(stock, period="2y", interval="1d"):
    try:
        data = yfinance.download(stock, period=period, interval=interval)
        data = data[['Open', 'High', 'Low', 'Close', 'Volume']] 
        return data
    except ValueError:
        pass

def zscore(series):
    return (series - series.mean()) / series.std()

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

def calculate_portfolio_sharpe(returns, volatilities, risk_free_rate = 0):
    weight = 1 / len(returns)
    weight_array = [weight] * len(returns)
    portfolio_ret = np.dot(returns, weight_array)
    portfolio_sd = np.sqrt(np.dot(np.square(volatilities), np.square(weight_array)))
    return (portfolio_ret - risk_free_rate) / portfolio_sd

def max_drawdown(returns):
    cumulative_returns = np.array(returns)
    peak = cumulative_returns[1]
    drawdown = 0
    max_drawdown = 0

    for i in range(2, len(cumulative_returns)):
        if cumulative_returns[i] > peak:
            peak = cumulative_returns[i]
        else:
            drawdown = (peak - cumulative_returns[i]) 
            if drawdown > max_drawdown:
                max_drawdown = drawdown

    return max_drawdown 

def plot_individual_pair_performance(pairs, returns, volatilites):
    bar_width = 0.5

    x = np.arange(len(pairs))
    fig, ax1 = plt.subplots()

    ax1.bar(x - bar_width/2, returns, width=bar_width, label='Percentage Return', color='blue')

    ax1.set_ylabel('Percentage Return', color='blue')

    ax2 = ax1.twinx()

    ax2.bar(x + bar_width/2, volatilites, width=bar_width, label='Volatility', color='red')

    ax2.set_ylabel('Volatility', color='red')


    plt.title('Comparison of Percentage Return and Volatility for each individual Pair')

    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')

    plt.show()
    
def calculate_sharpe_ratio(cumulative):
    cumulative_alloc = (1 + cumulative / 100)  
    daily = cumulative_alloc[1:].pct_change(1)
    avg_daily = daily[1:].mean()
    std = daily[1:].std()
    sharpe = np.sqrt(252) * avg_daily / std
    return sharpe

def calculate_spy_sharpe(spy_close):
    spy_returns = spy_close.pct_change()
    
    average_return = spy_returns.mean()
    std_dev = spy_returns.std()

    # Calculate the Sharpe ratio
    sharpe_ratio = np.sqrt(252) * (average_return) / std_dev

    return sharpe_ratio


def plot_total_portfolio_ret(equity_curves):
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
    spy_sharpe = calculate_spy_sharpe(spy)
    spy_daily_returns = spy.pct_change()
    spy_cum_daily_returns = (1 + spy_daily_returns).cumprod() - 1
    spy_cum_daily_returns.index = pd.to_datetime(spy_cum_daily_returns.index)  # Convert index to DatetimeIndex
    spy_cum_returns = spy_cum_daily_returns * 100
    spy_max_drawdown = max_drawdown(spy_cum_returns)
    sharpe = calculate_sharpe_ratio(cumulative_pct_returns)
     
    plt.plot(cumulative_pct_returns, color="blue", label="Portfolio Returns (%)")
    plt.plot([], [], ' ', label=f"Por. Max Drawdown: {max_draw:.2f}%")
    plt.plot([], [], ' ', label=f"Por. Sharpe Ratio: {sharpe:.2f}")
    plt.plot(spy_cum_returns, color="red", label="SPY Returns (%)")
    plt.plot([], [], ' ', label=f"SPY Max Drawdown: {spy_max_drawdown:.2f}%")
    plt.plot([], [], ' ', label=f"SPY. Sharpe Ratio: {spy_sharpe:.2f}")
    plt.title('Pairs Trading Portfolio Equity', fontsize=14, color='black')
    plt.xlabel('Time', fontsize=12)
    plt.ylabel('Percentage Return', fontsize=12)
    plt.xticks(fontsize=7)
    plt.legend(fontsize=7)
    plt.show()
    
    return sharpe
    

def write_results_to_file(resultsDict: dict, risk_free_rate = 0):
    path = "results.txt"
    cumulative_ret = 0
    vol_array = []
    ret_array = []
    equity_curves_array = []
    pairs = []
    with open(path, "w") as f:
        for pair, results in resultsDict.items():
            stock1Results = results[0]
            stock2Results = results[1]
            vol_array.append(stock1Results["Volatility (Ann.) [%]"]), vol_array.append(stock2Results["Volatility (Ann.) [%]"])
            cumulative_ret += (stock1Results["Return [%]"] + stock2Results["Return [%]"]) 
            ret_array.append(stock1Results["Return [%]"]), ret_array.append(stock2Results["Return [%]"])            
            stock1, stock2 = pair.split("/")[0], pair.split("/")[1]
            equity_curves_array.append(stock1Results['_equity_curve']), equity_curves_array.append(stock2Results['_equity_curve'])
            pairs.append(stock1), pairs.append(stock2)
            f.write(f"Pair: {pair} \n\n{stock1}:\n\n{stock1Results}\n\n{stock2}:\n\n{stock2Results}\n\n\n\n")
        cumulative_ret *= len(ret_array)
        # sharpe = calculate_portfolio_sharpe(ret_array, vol_array, risk_free_rate)
        portfolio_ret = calculate_portfio_returns(ret_array)
        sharpe = plot_total_portfolio_ret(equity_curves_array)
        plot_individual_pair_performance(pairs, ret_array, vol_array)
        f.write(f"Cumulative return ($): ${cumulative_ret}\n% return: {portfolio_ret}\nPortfolio sharpe ratio: {sharpe}\n")
