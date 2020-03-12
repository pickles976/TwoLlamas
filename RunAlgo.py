import alpaca_trade_api as tradeapi
import requests
import matplotlib.pyplot as mpl
import numpy as np
import statsStuff as stats

# Replace these with your API connection info from the dashboard
base_url = 'https://paper-api.alpaca.markets'
api_key_id = ''
api_secret = ''

api = tradeapi.REST(
    base_url=base_url,
    key_id=api_key_id,
    secret_key=api_secret
)

# We only consider stocks with per-share prices inside this range
min_share_price = 10.0
max_share_price = 500.0
# Minimum previous-day dollar volume for a stock we might consider
min_last_dv = 5000000

session = requests.session()

def get_tickers():
    print('Getting current ticker data...')
    tickers = api.polygon.all_tickers()
    print('Success.')
    assets = api.list_assets()
    symbols = [asset.symbol for asset in assets if asset.tradable]
    return [ticker for ticker in tickers if (
        ticker.ticker in symbols and
        ticker.lastTrade['p'] >= min_share_price and
        ticker.lastTrade['p'] <= max_share_price and
        ticker.prevDay['v'] * ticker.lastTrade['p'] > min_last_dv
    )]

tickers = get_tickers()

conn = tradeapi.StreamConn(base_url=base_url, key_id=api_key_id, secret_key=api_secret)

print("Finding stocks to channel trade")
i = 0
for ticker in tickers:
    symbol = ticker.ticker
    print(f"{i}/{len(tickers)}")
    l = stats.getTrendLines(symbol)
    i += 1
    if l != []:

        # retrieve price data
        allbars = api.get_barset(symbol, '5Min', limit=1000)
        bars = allbars[symbol]
        o = []  # open price data

        i = 0
        for bar in bars:  # get all opening price data
            i += 1
            o.append(bar.o)

        x = np.linspace(0, i, i)  # time axis values

        sellTolerance = 0.3
        buyTolerance = 0.1
        stopTolerance = 0.1

        channelWidth = (l[1] + 750 * l[0]) - (l[3] + 750 * l[2])

        rl = np.linspace(l[1], l[1] + i * l[0], i)  # creates array for line
        sl = np.linspace(l[3], l[3] + i * l[2], i)  # creates array for line

        buyPoint = l[3] + (buyTolerance * channelWidth)
        sellPoint = l[1] - (sellTolerance * channelWidth)
        stopPoint = l[3] - (stopTolerance * channelWidth)

        buyLine = np.linspace(buyPoint, buyPoint + i * l[2], i)  # creates array for line
        sellLine = np.linspace(sellPoint, sellPoint + i * l[0], i)  # creates array for line
        stopLine = np.linspace(stopPoint , stopPoint + i * l[2], i)  # creates array for line

        #REAL PRICE DATA AND TRENDLINES
        # fig, ax = mpl.subplots()
        # ax.plot(x, o)
        # ax.plot(x,rl, color='green')
        # ax.plot(x,sl, color='red')
        # ax.plot(x,buyLine, color='blue')
        # ax.plot(x,sellLine, color='yellow')
        # ax.plot(x,stopLine,color = 'black')
        # ax.set_title(f'Price Data {symbol}')
        # ax.set_xlabel('Time (5mins)')
        # ax.set_ylabel('Price (USD)')

        fig, ax = mpl.subplots()
        ax.plot(x[751:999], o[751:999])
        ax.plot(x[751:999], rl[751:999], color='green')
        ax.plot(x[751:999], sl[751:999], color='red')
        ax.plot(x[751:999], buyLine[751:999], color='blue')
        ax.plot(x[751:999], sellLine[751:999], color='yellow')
        ax.plot(x[751:999], stopLine[751:999], color='black')
        ax.set_title(f'Price Data {symbol}')
        ax.set_xlabel('Time (5mins)')
        ax.set_ylabel('Price (USD)')



mpl.show()

