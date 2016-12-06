import orm
from orm import Event, Logfile, EventType
import sources
import os
import logging
import time
import json
import utils

# fetch newest data into the DB
def refresh(sources_file, sources_dir, socketio):
    t_i = time.time()
    source_urls = sources.source_urls(sources_file)
    source_data = sources.source_data(sources_file)

    sources.download_sources(sources_file, sources_dir)

    new_events = []
    too_many_new_events = False

    with orm.get_session() as sess:
        for src in os.scandir(sources_dir):
            if not src.is_file() and src.name in source_data:
                expected_files = [sources.url_to_filename(x) for x in source_data[src.name]]
                logging.debug('scanning {} files, expect [{}]'.format(src.name, ','.join(expected_files)))
                for file in os.scandir(src.path):
                    if file.is_file() and file.name in expected_files:
                        logging.debug(file.path)

                        logfile = sess.query(Logfile).get(file.path)
                        if logfile == None:
                            logfile = Logfile(path=file.path, offset=0)
                            sess.add(logfile)

                        with open(logfile.path, 'rb') as f:
                            logging.debug('offset: {}'.format(logfile.offset))
                            f.seek(logfile.offset)
                            iter=0
                            for line in f:
                                try:
                                    data = utils.logline_to_dict(line.decode())
                                    if not ('type' in data and data['type'] == 'crash'):
                                        if 'milestone' in data:
                                            event = Event(type=EventType.milestone,
                                                          data=json.dumps(data),
                                                          time=utils.crawl_date_to_datetime(data['time']),
                                                          src_abbr=src.name,
                                                          src_url=source_urls[src.name])
                                        else:
                                            event = Event(type=EventType.game,
                                                          data=json.dumps(data),
                                                          time=utils.crawl_date_to_datetime(data['end']),
                                                          src_abbr=src.name,
                                                          src_url=source_urls[src.name])
                                        sess.add(event)
                                        if len(new_events)<100: # don't want to do huge sends over sockets TODO: make a config option
                                            new_events.append(event)
                                        else:
                                            too_many_new_events = True
                                except KeyError as e:
                                    logging.error('key {} not found'.format(e))
                                except Exception as e: # how scandelous! Don't want one broken line to break everything
                                    logging.exception('Something unexpected happened, skipping this event')
                                iter+= 1
                                logfile.offset+= len(line)
                                if iter%1000==0: #don't spam commits
                                    sess.commit()
                            logfile.offset = f.tell()
                            sess.commit()

    if len(new_events)>0 and not too_many_new_events:
        socketio.emit('crawlevent', json.dumps([e.getDict() for e in new_events]))

    logging.info('Refreshed in {} seconds'.format(time.time() - t_i))

def socketiotest(socketio):
    socketio.emit('crawlevent','[{"data": "test1"},{"data": "test2"}]')
