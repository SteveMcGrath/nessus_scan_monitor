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
from urllib2      import urlopen
from ConfigParser import ConfigParser


help_message = '''
The help message goes here.
'''

start   = re.compile(r'user \w+\s:\stesting\s([0-9.]+)')
finish  = re.compile(r'Finished testing ([0-9.]+).\sTime\s:\s([0-9.]+)')

def config(stanza, option):
  config = ConfigParser()
  config.read(os.path.join(sys.path[0],'config.ini'))
  return config.get(stanza, option)

class Usage(Exception):
  def __init__(self, msg):
    self.msg = msg

def watchfile(verbose, name, url):
  # Open the logfile and goto the end fo the file as it currently sits.  We
  # do not want old messages
  messages  = open(name, 'r')
  size      = os.stat(name)[6]
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
          print ip
          try:
            urlopen('%s/api/start/%s' % (url,ip))
          except:
            pass
      elif len(end) > 0:
        ip  = end[0][0]
        dur = end[0][1]
        if ip is not None and dur is not None:
          print ip, dur
          try:
            urlopen('%s/api/stop/%s' % (url,ip))
          except:
            pass

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

def main(argv=None):
  tailfile  = config('Client', 'watch_file')
  address   = config('Client', 'base_url')
  daemonize()
  watchfile(False, tailfile, address)

if __name__ == "__main__":
  sys.exit(main())
