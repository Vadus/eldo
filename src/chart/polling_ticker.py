import os, logging, threading

from poloniex import poloniex
from cmreslogging.handlers import CMRESHandler
from decimal import Decimal

elastic_host = os.getenv('ELASTIC_HOST', 'localhost')

#time to wait for the script after starting the program in seconds
WAIT_PERIOD = 5

handler = CMRESHandler(hosts=[{'host': elastic_host, 'port': 9200}],
                           auth_type=CMRESHandler.AuthType.NO_AUTH,
                           es_index_name="poloniex")
log = logging.getLogger()
log.setLevel(logging.INFO)
log.addHandler(handler)

def getTickerData():
    p = poloniex.poloniex("dunno", "what")
    ticker_data = p.returnTicker()
    print(ticker_data)
    
    for item in ticker_data:
    #     print item
        logItem = {'item': item.encode('ascii', 'replace')}
        for field in ticker_data[item]:
    #         print "\t" + field + ": %s"%(ticker_data[item][field])
            value = ticker_data[item][field]
            if not isinstance(value, int):
                value = value.encode('ascii', 'ignore')
                value = Decimal(value)
            logItem[field.encode('ascii', 'ignore')] = value
        logging.info(logItem, extra=logItem)

# entrypoint of script calls itself periodically via Timer call
# may drift a little bit in time see http://stackoverflow.com/a/18180189
def startPeriodicalRuntime():
    print("Calling Elastic. Next Call will be in %d seconds" %WAIT_PERIOD)
    threading.Timer( WAIT_PERIOD, startPeriodicalRuntime ).start()
    getTickerData()
    return

def start():
    startPeriodicalRuntime()