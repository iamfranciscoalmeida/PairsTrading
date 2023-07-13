# Pairs Trading Strategy using Linear Regression


## Description
This is a pairs trading strategy that takes a basket of stock tickers in the form of a .csv file, reads the file and finds all the pairs of stocks that are cointegrated with a positive correlation and that have a spread that is stationary in the long run and conducts a pairs trading strategy with buy and sell signals, as well as exit points. The steps are: 
1. Find cointegrated pairs of stocks and check for positive correlation. Add them to a dictionary of stocks where key == stock1 and value == list of all stocks that are cointegrated with stock1.
2. Backtest pairs of stocks with backtesting.py package. 
  - Calculate standardized spread of each pair of stocks using OLS. This spread follows a standard normal distribution: N(0, 1). This OLS also calculates the hedge ratio i.e. the slope of the regression line.
  - Create an indicator using this spread.
  - On each slice of data, check if spread > 1.5 or spread < -1.5
     - If spread > 1.5: long stock1 and short stock2.
     - If spread < -1.5: long stock2 and short stock1.
     - $Q_1 = \frac{cash}{100} \space \cdot \space (P_1 \space \cdot \space (1 + hedgeRatio))$
     - $Q_2 = \frac{cash \space \cdot \space hedgeRatio}{100} \space \cdot \space (P_2 \space \cdot \space (1 + hedgeRatio))$
  - After backtesting each stock, will calculate the portfolio's cumulative returns, percentage returns and sharpe ratio, written to an output file. 


## How to run
To run the backtest, either give as input a .csv file to read the stock tickers and find cointegrating pairs of stocks, input a dictionary with all the pairs as key, value pairs as described above, or input a list of tuples of all the pairs. 
Then, just run: 
```python
python pairs.py
```
or 
```python
python3 pairs.py
```
depending on your IDE. 
The results will be outputted into a .txt file as described above, with each pairs' individual performance as well as the portfolio performance.


## Portfolio of pairs and results
After conducting my own research, I created a portfolio of 29 pairs of stocks (can be found at the end of the ReadMe file) that are cointegrated and positively correlated. After optimizing parameters, I found that the hourly resolution works best for this strategy. 
The results can be seen below: 


## Portfolio returns against SPY - Stock Portfolio, Crypto Portfolio and Combined Portfolio
![Portolio Returns over the last year](./PortfolioStocks1y.png)
*Stock Portolio Returns over the last year*




![Stock Portolio Returns over the last two years](./PortfolioStocks2y.png)
*Stock Portolio Returns over the last year*




![Crypto Portolio Returns over the last year](./PortfolioCrypto1y.png)
*Crypto Portfolio Returns over the last year*




![Combined Portolio Returns over the last two years](./PortfolioCombined1y.png)
*Combined Stock & Crypto Portfolio Returns over the last year*

## Portfolio of pairs
After conducting research on stocks and cryptocurrencies in the same industry, I arrived to this list of pairs of stocks and cryptos that are cointegrated with at least a correlation of 0.5 and that have a spread that is stationary. This way, we can ensure that our portfolio is very diversified and avoids large market downswings. 


Stocks Portfolio
```python
(GOOG, AAPL)
(DOV, BA)
(VICI, VTR)
(VZ, PARA)
(TMUS, T)
(BBWI, BBY)
(BBWI, HD)
(CNC, DHR)
(CVS, DHR)
(EOG, COP)
(XEL, SRE)
(SRE, WEC)
(SRE, NEE)
(SRE, ES)
(SRE, AEP)
(SRE, DTE)
(SRE, DUK)
(SRE, LNT)
(AEP, DUK)
(HST, DLR)
(PLD, WELL)
(PSA, ESS)
(PSA, EXR)
(SLG, VNO)
(FCX, DD)
(AVY, AMT)
(CHRW, AMT)
(CMI, DE)
(CTAS, AME)
```


Crypto Portfolio
```python
(SNX-USD, XEM-USD)
(SNX-USD, ZRX-USD)
(SNX-USD, FIL-USD)
(SNX-USD, BAT-USD)
(SNX-USD, MANA-USD)
(SNX-USD, KSM-USD)
(SNX-USD, ADA-USD)
(SNX-USD, DOT-USD)
(SNX-USD, VET-USD)
(ETC-USD, XEM-USD)
(ETC-USD, ZEC-USD)
(ETC-USD, ZRX-USD)
(ETC-USD, FIL-USD)
(ETC-USD, BAT-USD)
(ETC-USD, MANA-USD)
(ETC-USD, KSM-USD)
(ETC-USD, ADA-USD)
(ETC-USD, XTZ-USD)
(ETC-USD, FTT-USD)
(XEM-USD, ZRX-USD)
(XEM-USD, FIL-USD)
(XEM-USD, BAT-USD)
(XEM-USD, MANA-USD)
(XEM-USD, KSM-USD)
(XEM-USD, ADA-USD)
(XEM-USD, DOT-USD)
(XEM-USD, LINK-USD)
(XEM-USD, VET-USD)
(XEM-USD, EOS-USD)
(XEM-USD, XTZ-USD)
(ZRX-USD, FIL-USD)
(ZRX-USD, BAT-USD)
(ZRX-USD, MANA-USD)
(ZRX-USD, KSM-USD)
(ZRX-USD, ADA-USD)
(ZRX-USD, DOT-USD)
(ZRX-USD, VET-USD)
(FIL-USD, OMG-USD)
(FIL-USD, ZRX-USD)
(FIL-USD, BAT-USD)
(FIL-USD, MANA-USD)
(FIL-USD, KSM-USD)
(FIL-USD, ADA-USD)
(FIL-USD, DOT-USD)
(FIL-USD, LINK-USD)
(FIL-USD, VET-USD)
(BAT-USD, MANA-USD)
(BAT-USD, KSM-USD)
(BAT-USD, ADA-USD)
(BAT-USD, DOT-USD)
(BAT-USD, LINK-USD)
(BAT-USD, VET-USD)
(BAT-USD, XTZ-USD)
(MANA-USD, DOT-USD)
(ETH-USD, TRX-USD)
(DOT-USD, VET-USD)
(LINK-USD, OMG-USD)
(LINK-USD, ZRX-USD)
(LINK-USD, FIL-USD)
(LINK-USD, BAT-USD)
(LINK-USD, MANA-USD)
(LINK-USD, VET-USD)
(LINK-USD, XTZ-USD)
(VET-USD, MANA-USD)
(VET-USD, DOT-USD)
(VET-USD, LINK-USD)
(EOS-USD, OMG-USD)
```