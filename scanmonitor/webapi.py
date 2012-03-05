from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bottle import Bottle, debug, request, response, template, run
import datetime
import os
import orm
try:
    import json
except:
    import simplejson as json


os.chdir(os.path.dirname(__file__))

app = Bottle()
engine = create_engine('sqlite:///database.db')
Session = sessionmaker(bind=engine)
