import alpaca_trade_api as tradeapi
import requests
import matplotlib.pyplot as mpl
from scipy.signal import butter, lfilter
import mpl_finance as plt
import time
from ta import trend
import pandas as pd
#import ta
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
from pytz import timezone

# Replace these with your API connection info from the dashboard
base_url = 'https://paper-api.alpaca.markets'
api_key_id = 'PK4VN0OM5UZRX207E6OG'
api_secret = 'pZg1i/jdoc8hPNbLCYTq7e6CrgUTKViScKTO6ZBG'

api = tradeapi.REST(
    base_url=base_url,
    key_id=api_key_id,
    secret_key=api_secret
)

#calculate simple moving average
def movingaverage(values,window):
    weights = np.repeat(1.0,window)/window
    smas = np.convolve(values,weights,'valid')
    return smas

#generate bandpass filter
def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

#apply filter to data
def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

session = requests.session()

#retrieve price data
bars = api.get_barset('AAPL', '5Min', limit=672)
aapl_bars = bars['AAPL']

o = [] #open price data

i = 0
for bar in aapl_bars: #get all opening price data
    i += 1
    o.append(bar.o)

sma = movingaverage(o,48)

x = np.linspace(0,i,i) #time axis values
#x *= 300 #300s converts 5min to hz
z = np.polyfit(x, o, 1) #returns slope and intercept
trend = np.linspace(z[1],z[1] + i * z[0],i) #creates array for line

flattened = o - trend #normalize stock price to trendline
flattened /= z[1] #get stock price as a percentage
flattened *= 100

# Sample rate and desired cutoff frequencies (in Hz).
#center frequency 0.00001388 Hz (20-hr period)
# or 0.004164 since we multiply by 300
fs = 2.0
lowcut = 0.003123
highcut = 0.005205

#filtered = butter_bandpass_filter(x, lowcut, highcut, fs, order=6)

variance = np.var(flattened) #calculate variance
print(variance)

fig, ax = mpl.subplots()
mpl.plot(x,flattened)
#mpl.plot(x,filtered)
#mpl.plot(x,o)
#mpl.plot(x, trend, '-')
# mpl.plot(sma)
mpl.show()