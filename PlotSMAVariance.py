import alpaca_trade_api as tradeapi
import requests
import matplotlib.pyplot as mpl
from scipy.signal import butter, lfilter
import numpy as np
from sklearn.linear_model import LinearRegression

vThresh = 0
plotting = True

# Replace these with your API connection info from the dashboard
base_url = 'https://paper-api.alpaca.markets'
api_key_id = 'PK4VN0OM5UZRX207E6OG'
api_secret = 'pZg1i/jdoc8hPNbLCYTq7e6CrgUTKViScKTO6ZBG'

api = tradeapi.REST(
    base_url=base_url,
    key_id=api_key_id,
    secret_key=api_secret
)

session = requests.session()

#find the zeros of a signal
def findZeros(signal,window):
    zeros = []
    zeros.append(0)
    for n in signal:
        index = np.where(signal == n)[0][0]
        #make sure that we can look ahead and behind
        if index > 0 and index < len(signal) - 1:
            #check if we have gone from negative to positive
            if (signal[index - 1] < 0 and signal[index + 1] > 0) or (signal[index - 1] > 0 and signal[index + 1] < 0):
                if abs(zeros[len(zeros) - 1] - index) > window:
                    zeros.append(index) #add the index of n to our list of zeros

    return zeros

#returns the x location of the max values
def findMaxs(signal,filtered,zeros):
    maxs = []

    for zero in zeros: #loop through all zeros
        index = zeros.index(zero)
        if filtered[zero + 1] - filtered[zero] > 0: #identify a positive slope
            if zeros.index(zero) < len(zeros) - 1:
                nextZero = zeros[index + 1]
                section = signal[zero:nextZero]
            else:
                section = signal[zero:len(signal) - 1]
            maxs.append( np.where(signal == max(section))[0][0] )

    return maxs

#returns the x location of the max values
def findMins(signal,filtered,zeros):
    mins = []

    for zero in zeros: #loop through all zeros
        index = zeros.index(zero)
        if filtered[zero + 1] - filtered[zero] < 0: #identify a positive slope
            if zeros.index(zero) < len(zeros) - 1:
                nextZero = zeros[index + 1]
                section = signal[zero:nextZero]
            else:
                section = signal[zero:len(signal) - 1]
            mins.append( np.where(signal == min(section))[0][0] )

    return mins

#generate bandpass filter
def butter_bandpass(lowcut, highcut, fs, order):
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

#returns the support and resistance lines for a
#stock with good potential for swing trading
def getTrendLines(symbol):

    #retrieve price data
    allbars = api.get_barset(symbol, '5Min', limit=1000)
    multOf5 = 1
    bars = allbars[symbol]
    barsPast = bars[0:700]
    barsFuture = bars[701:999]
    window = (60 / (5 * multOf5)) * (7)

    o = [] #open price data
    oPast = []
    oFuture = []

    i = 0
    for bar in barsPast: #get all opening price data
        i += 1
        o.append(bar.o)

    x = np.linspace(0,i,i) #time axis values
    z = np.polyfit(x, o, 1) #returns slope and intercept

    #if slope is negative throw it out
    # if z[0] < 0:
    #     return []

    trend = np.linspace(z[1],z[1] + i * z[0],i) #creates array for line

    flattened = o - trend #normalize stock price to trendline
    flattened /= z[1] #get stock price as a percentage
    flattened *= 100

    #center frequency 0.00001388 Hz (20-hr period)
    # or 0.004164 since we multiply by 300
    # Sample rate and desired cutoff frequencies (in Hz).
    fs = 0.00333 / multOf5
    corner = 0.0 #expand the sidelobe by this percentage
    #lowcut = 0.003123
    lowcut = 0.00001041 * (1 - corner) / multOf5
    #highcut = 0.005205
    highcut = 0.00001735 * (1 + corner) / multOf5
    filtered = butter_bandpass_filter(flattened, lowcut, highcut, fs, order=3)

    variance = np.var(flattened) #calculate variance

    #throw out if variance is too low
    if variance < vThresh:
        return []

    zeros = findZeros(filtered,window)
    maxes = findMaxs(flattened,filtered,zeros)
    mins = findMins(flattened,filtered,zeros)

    # if len(maxes) < 3 or len(mins) < 3:
    #     return []

    maxValues = []
    for max in maxes:
        maxValues.append(o[max])

    minValues = []
    for min in mins:
        minValues.append(o[min])

    rz = np.polyfit(maxes, maxValues, 1)  # returns slope and intercept
    resistance = np.linspace(rz[1], rz[1] + i * rz[0], i)  # creates array for line

    sz = np.polyfit(mins, minValues, 1)  # returns slope and intercept
    support = np.linspace(sz[1], sz[1] + i * sz[0], i)  # creates array for line

    # #throw out negative trendlines
    # if rz[0] < 0 or sz[0] < 0:
    #     return []
    #
    # #throw out if trendlines slopes intersect
    # if rz[0] < sz[0]:
    #     return []
    #
    # #throw out if trendline slope is too steep or too shallow
    # if rz[0] > 1 or rz[0] < 0.5 or sz[0] > 1 or sz[0] < 0.5:
    #     return []

    print(f"Variance is: {variance}")
    print(f"Zeros are: {zeros}")
    print(f"Peaks are at: {maxes}")
    print(maxValues)
    print(f"Valleys are at: {mins}")
    print(minValues)

    if plotting:

        fig, ax = mpl.subplots(1,2)

        #FILTERED AND NORMALIZED PRICE DATA
        ax[0].plot(flattened)
        ax[0].plot(filtered)
        ax[0].set_title(f'Normalized Price Data {symbol}')
        ax[0].set_xlabel('Time (5mins)')
        ax[0].set_ylabel('% change relative to opening price')

        #REAL PRICE DATA AND TRENDLINES
        ax[1].plot(x,o)
        ax[1].plot(maxes,maxValues,'go')
        ax[1].plot(mins,minValues,'ro')
        ax[1].plot(resistance,color = 'green')
        ax[1].plot(support,color = 'red')
        ax[1].set_title(f'Price Data {symbol}')
        ax[1].set_xlabel('Time (5mins)')
        ax[1].set_ylabel('Price (USD)')

    #flips the x so we can do linear regression and get the r2 value
    maxes = np.array(maxes).reshape((-1,1))
    modelMax = LinearRegression().fit(maxes,maxValues)
    rSQMax = modelMax.score(maxes,maxValues) ** 2
    print(f"Resistance R2 is: {rSQMax}")

    mins = np.array(mins).reshape((-1,1))
    modelMin = LinearRegression().fit(mins,minValues)
    rSQMin = modelMin.score(mins,minValues) ** 2
    print(f"Support R2 is: {rSQMin}")

    #throw our low correlation
    if rSQMax < 0.0 or rSQMin < 0.0:
        return []

    #return the slope and intercepts of our trendline
    return [ rz[0],rz[1],sz[0],sz[1] ]

symbol = 'NVDA'

l = getTrendLines(symbol)

# retrieve price data
allbars = api.get_barset(symbol, '5Min', limit=1000)
bars = allbars[symbol]
o = []  # open price data

i = 0
for bar in bars:  # get all opening price data
    i += 1
    o.append(bar.o)

x = np.linspace(0, i, i)  # time axis values

sellTolerance = 0.1
buyTolerance = 0.1
stopTolerance = 0.1

channelWidth = l[1] - l[3]

rl = np.linspace(l[1], l[1] + i * l[0], i)  # creates array for line
sl = np.linspace(l[3], l[3] + i * l[2], i)  # creates array for line

buyPoint = l[3] + (sellTolerance * channelWidth)
sellPoint = l[1] - (buyTolerance * channelWidth)
stopPoint = l[3] - (stopTolerance * channelWidth)

buyLine = np.linspace(buyPoint, buyPoint + i * l[2], i)  # creates array for line
sellLine = np.linspace(sellPoint, sellPoint + i * l[0], i)  # creates array for line
stopLine = np.linspace(stopPoint , stopPoint + i * l[2], i)  # creates array for line

# REAL PRICE DATA AND TRENDLINES
fig, ax = mpl.subplots()
ax.plot(x, o)
ax.plot(rl, color='green')
ax.plot(sl, color='red')
ax.plot(buyLine, color='blue')
ax.plot(sellLine, color='yellow')
ax.plot(stopLine,color = 'black')
ax.set_title(f'Price Data {symbol}')
ax.set_xlabel('Time (5mins)')
ax.set_ylabel('Price (USD)')

mpl.show()