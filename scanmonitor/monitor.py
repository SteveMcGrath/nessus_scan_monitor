import re
import os
import time
import urllib
import httplib
import logging
from logging.handlers import SysLogHandler, StreamHandler

# This code is to initiate the logger facility for generating syslog events.
logger = logging.getLogger()
logger.setLevel(logging.INFO)
syslog = SysLogHandler(address='/dev/log')
formatter = logging.Formatter('scanmon: %(levelname)s %(message)s')
syslog.setFormatter(formatter)
logger.addHandler(syslog)

def verbose():
    stream = StreamHandler()
    stream.setFormatter(formatter)
    logger.addHandler(stream)

class API(object):
    def __init__(self, host, port, key, ssl=False):
        self.host = host
        self.port = port
        self.key = key
        if ssl:
            self.conn = httplib.HTTPSConnection
        else:
            self.conn = httplib.HTTPConnection
    
    def _post(self, url, payload, headers={}):
        body = urllib.urlencode(payload)
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        headers['Content-Length'] = len(body)    
        try:
            http = self.conn(self.host, self.port)
            http.request('POST', url, body=body, headers=headers)
        except:
            logger.error('Could not send message to %s:%s' % (self.host, 
                                                              self.port))
    
    def start(self, ip):
        logger.info('Scanner started scanning %s' % ip)
        self._post('/api/start', {
            'api_key': self.api,
            'address': ip
        })
    
    def stop(self, ip):
        logger.info('Scanner stopped scanning %s' % ip)
        self._post('/api/stop', {
            'api_key': self.api,
            'address': ip
        })

def watch(filename, host, port, key):
    '''
    Designed to watch the nessusd.messages file from it's current location and
    send starts & stops to the central API as needed.
    '''    
    rstart = re.compile(r'user \w+\s:\stesting\s([0-9.]+)')
    rstop = re.compile(r'Finished testing ([0-9.]+).\sTime\s:')
    
    # Instantiate a new API object to talk to.
    api = API(host, port, key)
    
    # Open the nessusd.messages file and seek to the end of it.
    events = open(filename, 'r')
    size = os.stat(filename)[6]
    events.seek(size)
    
    while True:
        # Ask the file for its current size and attempt to read a line.  If 
        # we cant read a new line, then wait .1 seconds, then try again.
        size = events.tell()
        line = events.readline()
        if not line:
            time.sleep(0.1)
            events.seek(size)
        else:
            # Hey look, we got a log line!  Lets go ahead and parse this puppy
            # and see if we can get anything that we recognize.  If we do then
            # we will need to parse and send the events to the API.
            started = rstart.findall(line)
            if len(started) > 0:
                if started[0] is not None:
                    api.start(started[0])
            
            stopped = rstop.findall(line)
            if len(stopped) > 0:
                if started[0] is not None:
                    api.stop(started[0])
            