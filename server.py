import orm
from orm import Event, Logfile, EventType
from api import EventList
import sources
import os
import logging
import time
import json
import utils
from flask import Flask
from flask_restful import Resource, Api, reqparse
from flask_apscheduler import APScheduler

# settings TODO: move to settings file
SOURCES_FILE = 'sources.yml'
SOURCES_DIR = './sources'

if not os.path.isfile(SOURCES_FILE):
    SOURCES_FILE = 'sources_default.yml'

logging.basicConfig(level=logging.INFO)

class Config(object):
    JOBS = [
        {
            'id': 'refresh',
            'func': 'jobs:refresh',
            'args': (SOURCES_FILE, SOURCES_DIR),
            'trigger': 'interval',
            'seconds': 30,
            'max_instances': 1,
            'coalesce': True
        }
    ]

app = Flask(__name__)
app.config.from_object(Config())

api = Api(app)

api.add_resource(EventList, '/event')

if __name__=='__main__':
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true': # don't run again when werkzeug reloads due to files changing
        sched = APScheduler()
        sched.init_app(app)
        sched.start()
    app.run(debug=True)
