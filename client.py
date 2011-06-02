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
          urlopen('%s/api/start/%s' % (url,ip))
      elif len(end) > 0:
        ip  = end[0][0]
        dur = end[0][1]
        if ip is not None and dur is not None:
          print ip, dur
          urlopen('%s/api/stop/%s' % (url,ip))

def main(argv=None):
  verbose   = False
  tailfile  = config('Client', 'watch_file')
  address   = config('Client', 'base_url')
  if argv is None:
    argv = sys.argv
  try:
    try:
      opts, args = getopt.getopt(argv[1:], 'hf:r:v', 
                                 ['help', 'file=', 'remote=', 'verbose'])
    except getopt.error, msg:
      raise Usage(msg)
  
    # option processing
    for option, value in opts:
      if option in ('-v', '--verbose'):
        verbose   = True
      if option in ('-h', '--help'):
        raise Usage(help_message)
      if option in ('-f', '--file'):
        tailfile  = value
      if option in ('-r', '--remote'):
        address   = value
  
  except Usage, err:
    print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
    print >> sys.stderr, "\t for help use --help"
    return 2
  watchfile(verbose, tailfile, address)

if __name__ == "__main__":
  sys.exit(main())
