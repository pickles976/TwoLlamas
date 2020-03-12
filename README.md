# TwoLlamas
Swing trading bot

MUST USE PYTHON 3.7 WITH ANACONDA
runAlgo.py is the file to run.

This is a trading bot that uses the Alpaca API with the Polygon API's price data.
The idea is to use a bandpass filter to approximate price trends as a simple oscillating wave with a specified frequency, 
then use that approximation to predict high and low points and set trendlines. 
From there you can implement trading however you see fit.

1. Look through all available tickers and filters by volume, min price, and max price.
2. For each stock that matches our criteria, pull 1000 samples of 5-minute candlestick data. Perform analysis on the first 750 samples.
2. Use basic linear regression to find stocks with a positive trend and high variance.
3. Apply a bandpass filter to the price data. BPF has a center frequency of 1/20hrs (half a cycle is 10 hours of open market)
4. Use filtered signal to predict high and low sections of the price data, extract local max and min values for high and low sections
5. Plot simple linear regression on the peaks and valleys to build support and resistance lines. Throw out stocks with low r^2 values.
6. Throw out stocks with negative trendlines, converging trendlines, or too few sample points.
7. Set stop, buy, and sell lines within the channel. Overlay these onto the last 250 samples of price data to see theoretical performance


