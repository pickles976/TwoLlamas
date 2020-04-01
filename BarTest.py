import alpaca_trade_api as tradeapi
import requests
import matplotlib.pyplot as mpl
import mpl_finance as plt
import time
from ta import trend
import numpy as np
from datetime import datetime, timedelta
from pytz import timezone

# Replace these with your API connection info from the dashboard
base_url = 'https://paper-api.alpaca.markets'
api_key_id = ''
api_secret = ''

api = tradeapi.REST(
    base_url=base_url,
    key_id=api_key_id,
    secret_key=api_secret
)

session = requests.session()

bars = api.get_barset('AAPL', '5Min', limit=672)
aapl_bars = bars['AAPL']

t = []
o = []
c = []
h = []
l = []

for bar in aapl_bars:
    t.append(bar.t)
    o.append(bar.o)
    c.append(bar.c)
    h.append(bar.h)
    l.append(bar.l)

fig, ax = mpl.subplots()
plt.candlestick2_ochl(ax,o,c,h,l,1)
mpl.show()
