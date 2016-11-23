import orm
from orm import Event, Logfile, TypeEnum
import sources
import os
import logging
import time
import json
import utils
from datetime import datetime

logging.basicConfig(level=logging.DEBUG)

SOURCES_FILE = 'sources.yml'
SOURCES_DIR = './sources'

def refresh():
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
    sess = orm.get_session()

    if not os.path.isfile(SOURCES_FILE):
        sources_file = 'sources_default.yml'

    refresh()
