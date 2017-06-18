import os, time, logging, threading

from poloniex import poloniex
from cmreslogging.handlers import CMRESHandler
from decimal import Decimal

elastic_host = os.getenv('ELASTIC_HOST', 'localhost')

#time to wait for the script after starting the program in seconds
WAIT_PERIOD = 300 #5 minutes

handler = CMRESHandler(hosts=[{'host': elastic_host, 'port': 9200}],
                           auth_type=CMRESHandler.AuthType.NO_AUTH,
                           es_index_name="poloniex")
log = logging.getLogger()
log.setLevel(logging.INFO)
log.addHandler(handler)


def to_decimal(value):
    if not isinstance(value, int) and not isinstance(value, float):
        value = value.encode('ascii', 'ignore')
        value = Decimal(value)
    elif isinstance(value, float):
        value = Decimal(value)
    return value

def to_dateString(value):
    if value == 0:
        value = int(time.time())
    return time.strftime('%Y-%m-%dT%H:%M:%S', (time.gmtime(value)))

def getTickerData():
    p = poloniex.poloniex("dunno", "what")
    ticker_data = p.returnTicker()
    print(ticker_data)
    
    for item in ticker_data:
    #     print item
        currencyPair = item.encode('ascii', 'replace')
        logItem = {'item': currencyPair}
        for field in ticker_data[item]:
    #         print "\t" + field + ": %s"%(ticker_data[item][field])
            value = ticker_data[item][field]
            value = to_decimal(value)
            logItem[field.encode('ascii', 'ignore')] = value
        
        chart_data = p.returnChartData(currencyPair)
        for field in chart_data[0]:
            value = chart_data[0][field]
            if field == 'date':
                value = to_dateString(value)
            else:
                value = to_decimal(value)
            logItem[field.encode('ascii', 'ignore')] = value
        
        print logItem
        logging.info(logItem, extra=logItem)
        time.sleep(1)

             

# entrypoint of script calls itself periodically via Timer call
# may drift a little bit in time see http://stackoverflow.com/a/18180189
def startPeriodicalRuntime():
    print("Calling Elastic. Next Call will be in %d seconds" %WAIT_PERIOD)
    threading.Timer( WAIT_PERIOD, startPeriodicalRuntime ).start()
    getTickerData()
    return

def start():
    startPeriodicalRuntime()