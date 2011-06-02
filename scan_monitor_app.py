from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy                 import Table, Column, Integer, String, \
                                       DateTime, Date, ForeignKey, \
                                       Boolean, create_engine, MetaData, \
                                       and_, or_, desc
from sqlalchemy.orm             import relation, backref, sessionmaker
from ConfigParser               import ConfigParser
from bottle                     import route, run, debug, template, request
import os
import sys
import datetime
import json

def config(stanza, option):
  config = ConfigParser()
  config.read('config.ini')
  return config.get(stanza, option)

Base        = declarative_base()
engine      = create_engine(config('Database', 'DBString'))
Session     = sessionmaker(bind=engine)
scanners    = config('Settings','Scanners').split(',')

class Host(Base):
  __tablename__ = 'hosts'
  address       = Column(String(16), primary_key=True)
  duration      = Column(Integer)
  started       = Column(DateTime)
  stopped       = Column(DateTime)
  
  def __init__(self, address):
    self.address  = address
    self.started  = datetime.datetime.now()
  
  def finished(self):
    self.stopped  = datetime.datetime.now()
    self.duration = (self.stopped - self.started).seconds
    

@route('/api/start/:ip', method='GET')
def start_scan(ip):
  if request.environ.get('REMOTE_ADDR') in scanners:
    session = Session()
    session.query(Host).filter_by(address=ip).delete()
    session.add(Host(ip))
    session.commit()
    session.close()

@route('/api/stop/:ip', method='GET')
def stop_scan(ip):
  if request.environ.get('REMOTE_ADDR') in scanners:
    session = Session()
    host    = session.query(Host).filter_by(address=ip).one()
    host.finished()
    session.merge(host)
    session.commit()
    session.close()

@route('/api/active')
def show_active():
  session = Session()
  hosts   = session.query(Host).filter_by(stopped=None).all()
  resp    = []
  for host in hosts:
    resp.append({
       'address': host.address,
       'started': host.started.strftime('%D %H:%M'),
      'duration': (datetime.datetime.now() - host.started).seconds
    })
  return json.dumps(resp)

@route('/api/show/:ip', method='GET')
def show_ip(ip):
  session = Session()
  try:
    host    = session.query(Host).filter_by(address=ip).one()
  except:
    return None
  else:
    return json.dumps({
    'address': host.address,
    'started': host.started.strftime('%D %H:%M'),
    'stopped': host.stopped.strftime('%D %H:%M'),
    'duration': (host.stopped - host.started).seconds
    })

@route('/', method='GET')
@route('/', method='POST')
def home_page():
  active_hosts = json.loads(show_active())
  if request.POST.get('lookup','').strip():
    address       = request.POST.get('address','').strip()
    searched      = True
    session       = Session()
    search_hosts  = session.query(Host).filter(and_(Host.stopped != None, Host.address.like('%' + address + '%'))).all()
  else:
    searched      = False
    search_hosts  = []
  return template('main_page', active_hosts=active_hosts, searched=searched, 
                  search_hosts=search_hosts)

if __name__ == '__main__':
  debug(True)
  Host.metadata.create_all(engine)
  run(port=int(config('Settings', 'Port')), host=config('Settings', 'Host'))