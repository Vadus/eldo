import os, time, logging, requests, json

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


def alreadyExists(chartItemId):
    query = json.dumps({
          "query": {
              "match" : { "chartItemId" : "%s"%chartItemId }
          }
    })
    
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    response = requests.post('http://' + elastic_host + ':9200/_search', data=query, headers=headers)
    result = json.loads(response.text)
    
    amount = result["hits"]["total"]
    if amount > 0:
        return True
    
    return False

def getTickerData(chartDataAge = 300):
    p = poloniex.poloniex("dunno", "what")
    ticker_data = p.returnTicker()
    print(ticker_data)
    
    for item in ticker_data:
    #     print item
        currencyPair = item.encode('ascii', 'replace')
        logItem = {'item': currencyPair, 'ticker_date': to_dateString(0)}
        for field in ticker_data[item]:
            #print "\t Ticker:" + field + ": %s"%(ticker_data[item][field])
            value = ticker_data[item][field]
            value = to_decimal(value)
            logItem[field.encode('ascii', 'ignore')] = value
        
        chart_data = p.returnChartData(currencyPair, chartDataAge)
        openValue = Decimal('0')
        closeValue = Decimal('0')
        for chart_data_line in chart_data:
            chartItem = logItem.copy()
            for field in chart_data_line:
                value = chart_data_line[field]
                if field == 'date':
                    chartItem['chartItemId'] = chartItem['item'] + '_' + str(value)
                    value = to_dateString(value)
                else:
                    value = to_decimal(value)
                    if field == 'open':
                        openValue = value
                    elif field == 'close':
                        closeValue = value
                
                chartItem[field.encode('ascii', 'ignore')] = value
            try:    
                if alreadyExists(chartItem['chartItemId']):
                    print('Found data that already exists for chartItemId %s with open %d, close %d'%(chartItem['chartItemId'], openValue, closeValue))
                    continue
            except KeyError:
                continue
        
            if openValue > 0:
                chartItem['change'] = ((closeValue - openValue) / openValue) * 100
            else:
                chartItem['change'] = Decimal('0');
            
            print chartItem
            
            log.addHandler(handler)
            logging.info(chartItem, extra=chartItem)
            log.removeHandler(handler)
            
        time.sleep(0.2)
