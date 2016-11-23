import orm
from orm import Event, Logfile, TypeEnum
import sources
import os
import logging
import time
import json
import utils
from flask import Flask
from flask_restful import Resource, Api, reqparse

# settings TODO: move to settings file
SOURCES_FILE = 'sources.yml'
SOURCES_DIR = './sources'
PAGE_LIMIT = 1000

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# API section
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('offset', type=int)
parser.add_argument('limit', type=int)

default_ok_result = {'status': 200, 'message': 'OK'}

class EventList(Resource):
    def get(self):
        offset = 0
        limit = PAGE_LIMIT
        args = parser.parse_args()
        if args['offset']!=None: offset = args['offset']
        if args['limit']!=None and args['limit'] < PAGE_LIMIT: limit = args['limit']
        sess = orm.get_session()
        q = sess.query(Event).offset(offset).limit(limit)
        result = default_ok_result.copy()
        result.update({'offset': offset, 'count': q.count(), 'results': [e.getDict() for e in q.all()]})
        return result

api.add_resource(EventList, '/event')

# fetch newest data into the DB
def refresh():
    sess = orm.get_session()
    source_urls = sources.source_urls(SOURCES_FILE)

    t_i = time.time()
    sources.download_sources(SOURCES_FILE, SOURCES_DIR)
    logging.info('Done downloading in {} seconds'.format(time.time() - t_i))

    for src in os.scandir(SOURCES_DIR):
        if not src.is_file():
            logging.debug('scanning {} files'.format(src.name))
            for file in os.scandir(src.path):
                if file.is_file():
                    logging.debug(file.path)

                    logfile = sess.query(Logfile).get(file.path)
                    if logfile == None:
                        logfile = Logfile(path=file.path, offset=0)
                        sess.add(logfile)

                    with open(logfile.path) as f:
                        logging.debug('offset: {}'.format(logfile.offset))
                        f.seek(logfile.offset)
                        for line in f:
                            data = utils.logline_to_dict(line)
                            try:
                                if not ('type' in data and data['type'] == 'crash'):
                                    if 'milestone' in data:
                                        event = Event(type=TypeEnum.milestone,
                                                      data=json.dumps(data),
                                                      time=utils.crawl_date_to_datetime(data['time']),
                                                      src_abbr=src.name,
                                                      src_url=source_urls[src.name])
                                    else:
                                        event = Event(type=TypeEnum.game,
                                                      data=json.dumps(data),
                                                      time=utils.crawl_date_to_datetime(data['end']),
                                                      src_abbr=src.name,
                                                      src_url=source_urls[src.name])
                                    sess.add(event)
                            except KeyError as e:
                                logging.error('key {} not found in {}'.format(e, data))
                        logfile.offset = f.tell()
    sess.commit()

if __name__=='__main__':
    if not os.path.isfile(SOURCES_FILE):
        sources_file = 'sources_default.yml'

    refresh()

    app.run(debug=True)
