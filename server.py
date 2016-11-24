from api import EventList
import os
import logging
from flask import Flask
from flask_restful import Resource, Api, reqparse
from flask_apscheduler import APScheduler
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)
api = Api(app)

# settings TODO: move to settings file
SOURCES_FILE = 'sources.yml'
SOURCES_DIR = './sources'

if not os.path.isfile(SOURCES_FILE):
    SOURCES_FILE = 'sources_default.yml'

logging.basicConfig(level=logging.INFO)

class Config(object):
    JOBS = [
        # {
        #     'id': 'socketiotest',
        #     'func': 'jobs:socketiotest',
        #     'args': (socketio,),
        #     'trigger': 'interval',
        #     'seconds': 10,
        #     'max_instances': 1,
        #     'coalesce': True
        # },
        {
            'id': 'refresh',
            'func': 'jobs:refresh',
            'args': (SOURCES_FILE, SOURCES_DIR, socketio),
            'trigger': 'interval',
            'seconds': 30,
            'max_instances': 1,
            'coalesce': True
        }
    ]

app.config.from_object(Config())

@app.route('/')
def hello_world():
    return 'Hello, World!'

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
            console.log('got crawlevent');
            data = JSON.parse(data);
            data.forEach(function(event) {
                document.getElementById("eventlist").innerHTML+="<li>"+JSON.stringify(event)+"</li>";
            });
        });
    </script>
    <body><ul id="eventlist"></ul></body>
    """

api.add_resource(EventList, '/event')

if __name__=='__main__':
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true': # don't run again when werkzeug reloads due to files changing
        sched = APScheduler()
        sched.init_app(app)
        sched.start()
    socketio.run(app)
    app.run(debug=True)
