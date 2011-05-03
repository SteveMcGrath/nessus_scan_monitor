#!/usr/bin/env python
# encoding: utf-8
"""
scan_monitor_server.py

Created by Steven McGrath on 2011-05-03.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import os
import datetime
import json
from SimpleXMLRPCServer         import SimpleXMLRPCServer
from SimpleXMLRPCServer         import SimpleXMLRPCRequestHandler
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy                 import Table, Column, Integer, String, \
                                       DateTime, Date, ForeignKey, \
                                       Boolean, create_engine, MetaData, and_
from sqlalchemy.orm             import relation, backref, sessionmaker

Base      = declarative_base()
engine      = create_engine('sqlite:///database.db')
Session     = sessionmaker(bind=engine)

class Host(Base):
  __tablename__ = 'hosts'
  id            = Column(Integer(10), primary_key=True)
  address       = Column(String(15))
  started       = Column(DateTime)
  stopped       = Column(DateTime)
  duration      = Column(Integer(6))
  
  def __init__(self, address):
    self.address  = address
    self.started  = datetime.datetime.now()
  
  def finished(self, duration):
    self.stopped  = datetime.datetime.now()
    self.duration = duration

class RequestHandler(SimpleXMLRPCRequestHandler):
  rpc_paths       = ('/RPC2',)

class NetworkFunctions(object):
  hosts           = {}
  
  def add(self, ip):
    session       = Session()
    host          = Host(ip)
    session.add(host)
    session.commit()
    self.hosts[ip] = host.id
    return True
  
  def finish(self, ip, duration):
    session       = Session()
    host          = session.query(Host).filter(Host.id == self.hosts[ip]).one()
    host.finished(duration)
    session.commit()
    self.hosts.pop(ip)
    return True
  
  def current(self):
    return json.dumps(self.hosts.keys())
    
def daemonize():
  pidfile = '/var/run/nessus_monitor.pid'
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
  out_log = file('/var/log/nessus_monitor.log', 'a+')
  err_log = file('/var/log/nessus_monitor.err', 'a+', 0)
  dev_null = file('/dev/null', 'r')
  os.dup2(out_log.fileno(),   sys.stdout.fileno())


def main():
  Host.metadata.create_all(engine)
  address = '0.0.0.0'
  port    = 10240
  server  = SimpleXMLRPCServer((address, port), 
                               requestHandler=RequestHandler,
                               logRequests=False)
  server.register_introspection_functions()
  server.register_instance(NetworkFunctions())
  #daemonize()
  server.serve_forever()

if __name__ == '__main__':
  sys.exit(main())

