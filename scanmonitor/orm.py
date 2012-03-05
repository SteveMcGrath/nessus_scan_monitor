from sqlalchemy import (Table, Column, Integer, String, DateTime, Date, 
                        ForeignKey, Text, Boolean, MetaData, 
                        and_, desc, create_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (backref, joinedload, subqueryload, sessionmaker,
                            relationship)
import datetime
from hashlib import md5

Base = declarative_base()

def init(engine):
    Host.metadata.create_all(engine)

class Host(Base):
    __tablename__ = 'hosts'
    id = Column(Integer(10), primary_key=True)
    address = Column(String(16))
    start_time = Column(DateTime)
    stop_time = Column(DateTime)
    scanner_id = ForeignKey('scanners.id')
    active = Column(Boolean)
    scanner = relationship(Scanner, backref='hosts')
    
    def __init__(self, address):
        current = datetime.datetime.now()
        self.address = address
        self.active = True
        self.start_time = current
        self.stop_time = None
    
    def stop(self):
        self.active = False
        self.stop_time = datetime.datetime.now()
    
    def duration(self):
        current = datetime.datetime.now()
        if self.active:
            duration = (current - self.start_time).seconds
        else:
            duration = (self.stop_time - self.start_time).seconds
        return duration

class Scanner(Base):
    __tablename__ = 'scanners'
    id = Column(String(32), primary_key=True)
    name = Column(String(128))
    address = Column(String(16))
    
    def __init__(self, name, address):
        h = md5()
        h.update(datetime.datetime.now().ctime())
        h.update(name)
        h.update(address)
        self.id = h.hexdigest()
        self.name = name
        self.address = address