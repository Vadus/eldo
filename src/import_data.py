import sys
from chart import polling_ticker

if len(sys.argv) > 1:
    polling_ticker.getTickerData(int(sys.argv[1]))
else:
    polling_ticker.getTickerData(300)
    