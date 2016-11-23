import orm
from orm import Event, Logfile, TypeEnum
import sources
import os
import logging
import time
import json
import utils

# fetch newest data into the DB
def refresh(sources_file, sources_dir):
    t_i = time.time()
    sess = orm.get_session()
    source_urls = sources.source_urls(sources_file)

    sources.download_sources(sources_file, sources_dir)

    for src in os.scandir(sources_dir):
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
                            except Exception as e: # how scandelous!
                                logging.exception('Something unexpected happened, skipping this event')
                        logfile.offset = f.tell()
                    sess.commit()
    logging.info('Refreshed in {} seconds'.format(time.time() - t_i))