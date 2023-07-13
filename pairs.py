""""Goal: to input a list of stocks, find two stocks that correlate, and find the point at which to execute a trade: 
        - short 
        - long
"""
from cointegration import *
from pairs_strategy import *
import time


if __name__ == "__main__":
    start_time = time.time()
    stocks = read_sp500_tickers("newtickers.csv")
    cointegrated_stocks = find_cointegrated_stocks(stocks)
    print(cointegrated_stocks)
    # cointegrated_stocks = {'GOOG': ['AAPL'], 'DOV': ['BA'], 'VICI': ['VTR'], 'VZ': ['PARA'], 'TMUS': ['T'], 'BBWI': ['BBY', 'HD'], 'CNC': ['DHR'], 'CVS': ['DHR'], 'EOG': ['COP'], 'XEL': ['SRE'], 'SRE': ['WEC', 'NEE', 'ES', 'AEP', 'DTE', 'DUK', 'LNT'], 'AEP': ['DUK']}


    # results = {}
    # for key, value in cointegrated_stocks.items():
    #     stock1 = key
    #     for stock2 in value:
    #         results1, results2 = backtest_pairs(stock1, stock2, period="1y")
    #         results_key = f"{stock1}/{stock2}"
    #         results[results_key] = [results1, results2]
            
    # write_results_to_file(results)
    end_time = time.time()
    time_taken = round(end_time - start_time, 2)
    print(f"--------Time taken {time_taken}s--------")