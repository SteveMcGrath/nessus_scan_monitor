#!/usr/bin/env python
# encoding: utf-8
"""
client.py

Created by Steven McGrath on 2011-05-03.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import os
import time
import re
import httplib
from ConfigParser import ConfigParser

# These flags are overriden by the config file.
VERBOSE = False
DAEMON = True

# Regexes used to determine when a scan has started or stopped.
start = re.compile(r'user \w+\s:\stesting\s([0-9.]+)')
finish = re.compile(r'Finished testing ([0-9.]+).\sTime\s:\s([0-9.]+)')

# The configuration file parser ;)
config = ConfigParser()
config.read(os.path.join(sys.path[0],'config.ini'))

class API(object):
  def __init__(self, host, ssl=False):
    self.host = host
    if ssl:
      self.conn = httplib.HTTPSConnection
    else:
      self.conn = httplib.HTTPConnection
  
  def _get(self, url):
    http = self.conn(self.host)
    http.request('GET', url)
  
  def start(self, ip):
    url = '/api/start/%s' % ip
    if VERBOSE:
      print url
    self._get(url)
  
  def stop(self, ip):
    url = '/api/stop/%s' % ip
    if VERBOSE:
      print url
    self._get(url)

def daemonize():
  pidfile = '/var/run/service_light.pid'
  # do the UNIX double-fork magic, see Stevens' "Advanced 
  # Programming in the UNIX Environment" for details (ISBN 0201563177)
  try: 
    pid = os.fork() 
    if pid > 0:
      # exit first parent
      sys.exit(0) 
  except OSError, e: 
    print >>sys.stderr, "fork #1 failed: %d (%s)" % (e.errno, e.strerror) 
    sys.exit(1)
  # decouple from parent environment
  os.chdir("/") 
  os.setsid() 
  os.umask(0) 
  # do second fork
  try: 
    pid = os.fork() 
    if pid > 0:
      # exit from second parent, print eventual PID before
      #print "Daemon PID %d" % pid
      open(pidfile, 'w').write('%d' % pid)
      sys.exit(0) 
  except OSError, e: 
    print >>sys.stderr, "fork #2 failed: %d (%s)" % (e.errno, e.strerror) 
    sys.exit(1) 
  # Redirect all console data to logfiles
  out_log = file('/var/log/service_light.log', 'a+')
  err_log = file('/var/log/service_light.err', 'a+', 0)
  dev_null = file('/dev/null', 'r')
  os.dup2(out_log.fileno(),   sys.stdout.fileno())

def watchfile(verbose, name, api):
  # Open the logfile and goto the end fo the file as it currently sits.  We
  # do not want old messages
  messages = open(name, 'r')
  size = os.stat(name)[6]
  messages.seek(size)  
  
  while True:
    where   = messages.tell()
    line    = messages.readline()
    if not line:
      time.sleep(1)
      messages.seek(where)
    else:
      new   = start.findall(line)
      end   = finish.findall(line)
      if len(new) > 0:
        ip  = new[0]
        if ip is not None:
            api.start(ip)
      elif len(end) > 0:
        ip  = end[0][0]
        dur = end[0][1]
        if ip is not None and dur is not None:
            api.stop(ip)

def main(argv=None):
  tailfile  = config.get('Client', 'watch_file')
  host      = config.get('Client', 'host')
  ssl       = config.getboolean('Client', 'ssl')
  DAEMON    = config.getboolean('Client', 'daemonize')
  VERBOSE   = config.getboolean('Client', 'verbose')
  api       = API(host, ssl)
  
  if DAEMON:
    daemonize()
  watchfile(False, tailfile, api)

if __name__ == "__main__":
  sys.exit(main())
