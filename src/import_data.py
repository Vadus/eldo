import sys
from chart import polling_ticker

if len(sys.argv) > 1:
    polling_ticker.importData(int(sys.argv[1]))
else:
    polling_ticker.importData(300)
    