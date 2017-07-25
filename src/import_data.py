#!/usr/bin/python

from chart import polling_ticker
import time

actualSecond = int(time.strftime('%S', (time.gmtime())))
restSeconds = 60 - actualSecond;
#print 'actual second: %d, rest seconds until next minute %d'%(actualSecond, restSeconds)
if restSeconds >= 10:
    times = int(restSeconds / 10.0 + 0.5)
    #print 'polling %d times'%times
    for i in range(times):
        #print 'polling... at %s'%time.strftime('%Y-%m-%dT%H:%M:%S', (time.localtime()))
        polling_ticker.getTickerData()
        time.sleep(10)
