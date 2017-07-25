import os, time, logging, requests, json

from poloniex import poloniex
from cmreslogging.handlers import CMRESHandler
from decimal import Decimal

elastic_host = os.getenv('ELASTIC_HOST', 'localhost')

handler = CMRESHandler(hosts=[{'host': elastic_host, 'port': 9200}],
                           auth_type=CMRESHandler.AuthType.NO_AUTH,
                           es_index_name="poloniex")
log = logging.getLogger()
log.setLevel(logging.INFO)

def findPrevLastValue(item):
    try:
        query = json.dumps({
            "size": 1,
            "query": {
                "match": {"item": "%s"%item}
            },
            "sort": { "timestamp": { "order": "desc" }}
        })
        
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        response = requests.post('http://' + elastic_host + ':9200/poloniex-*/_search', data=query, headers=headers)
        result = json.loads(response.text)
        #print result
        
        if len(result['hits']['hits']) > 0:
            prevLastValue = to_decimal(result['hits']['hits'][0]['_source']['last'])
            #print prevLastValue
            return prevLastValue
        
    except requests.exceptions.ConnectionError:
        return Decimal(0)
    
    return Decimal(0)

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
        #print item
        currencyPair = item.encode('ascii', 'replace')
        logItem = {'item': currencyPair, 'ticker_date': to_dateString(0)}
        for field in ticker_data[item]:
            #print "\t" + field + ": %s"%(ticker_data[item][field])
            value = ticker_data[item][field]
            value = to_decimal(value)
            logItem[field.encode('ascii', 'ignore')] = value
        
            if field == 'last':
                prevLastValue = findPrevLastValue(item)
                if prevLastValue > 0:
                    logItem['change'] = ((value - prevLastValue) / prevLastValue) * 100
                else:
                    logItem['change'] = Decimal('0');
        
        print logItem
        log.addHandler(handler)
        logging.info(logItem, extra=logItem)
        log.removeHandler(handler)
    