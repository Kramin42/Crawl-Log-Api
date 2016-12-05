from api import EventList
import os
import logging
import yaml
from flask import Flask
from flask_restful import Resource, Api, reqparse
from flask_apscheduler import APScheduler
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, engineio_logger=True)
api = Api(app)

SOURCES_DIR = './sources'
CONFIG_FILE = 'config.yml'
if not os.path.isfile(CONFIG_FILE):
    CONFIG_FILE = 'config_default.yml'

CONFIG = yaml.safe_load(open(CONFIG_FILE, encoding='utf8'))

logging_level = logging.NOTSET
if 'logging level' in CONFIG and hasattr(logging, CONFIG['logging level']):
    logging_level = getattr(logging, CONFIG['logging level'])

logging.basicConfig(level=logging_level)

app.config['JOBS'] = []
for job in CONFIG['refresh schedule']:
    app.config['JOBS'].append({
        'id': 'refresh '+job['sources file'],
        'func': 'jobs:refresh',
        'args': (job['sources file'], SOURCES_DIR, socketio),
        'trigger': 'interval',
        'seconds': job['interval'],
        'max_instances': 1,
        'coalesce': True
    })

@app.route('/')
def hello_world():
    return """A PubSub utility for crawl milestones<br/>
    <a href="https://github.com/Kramin42/Crawl-PubSub">Source/Documentation</a><br/>
    <a href="/socketiotest">Live milestone example</a>
    """

@app.route('/socketiotest')
def socketiotest():
    return r"""
    <script type="text/javascript" src="//cdnjs.cloudflare.com/ajax/libs/socket.io/1.3.6/socket.io.min.js"></script>
    <script type="text/javascript" charset="utf-8">
        var socket = io.connect('http://' + document.domain + ':' + location.port);
        socket.on('connect', function() {
            document.getElementById("eventlist").innerHTML+="<li>connected</li>";
        });
        socket.on('crawlevent', function(data) {
            data = JSON.parse(data);
            data.forEach(function(event) {
                document.getElementById("eventlist").innerHTML+="<li>"+JSON.stringify(event)+"</li>";
            });
        });
    </script>
    <ul id="eventlist"></ul>
    """

api.add_resource(EventList, '/event')

if __name__=='__main__':
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true': # don't run again when werkzeug reloads due to files changing
        sched = APScheduler()
        sched.init_app(app)
        sched.start()
    app.run(host=CONFIG['host'], port=CONFIG['port'])
