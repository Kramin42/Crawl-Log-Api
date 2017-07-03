import orm
import time
import logging
from orm import Event, EventType
from flask_restful import Resource, Api, reqparse

from sqlalchemy.dialects import sqlite

logger = logging.getLogger('api')
logger.setLevel(logging.DEBUG)

parser = reqparse.RequestParser()
parser.add_argument('offset', type=int)
parser.add_argument('limit', type=int)
parser.add_argument('type', type=EventType)
parser.add_argument('src')
parser.add_argument('reverse')

default_ok_result = {'status': 200, 'message': 'OK'}

class EventList(Resource):
    def get(self):
        t_i = time.time()
        offset = 0
        limit = 1000
        args = parser.parse_args()
        logger.debug(args)
        if args['offset']!=None: offset = args['offset']
        if args['limit']!=None and args['limit'] < 1000: limit = args['limit'] # TODO: make  max limit a config option
        with orm.get_session() as sess:
            q = sess.query(Event)
            if args['type']!=None: q = q.filter_by(type=args['type'])
            if args['src']!=None: q = q.filter_by(src_abbr=args['src'])
            if args['reverse']==None:  # cant offset when reversed
                q = q.filter(Event.id >= offset)
            else:
                q = q.order_by(Event.id.desc())
            q = q.limit(limit)
            result = default_ok_result.copy()

            qstring = str(q.statement.compile(dialect=sqlite.dialect(),
                                compile_kwargs={"literal_binds": True})).replace('\n','')
            logger.debug("DB Query: {}".format(qstring))

            es = q.all()
            logger.debug('queried db in {} seconds.'.format(time.time()-t_i))
            result.update({'offset': offset, 'next_offset': (es[-1].id+1 if len(es)>0 else offset), 'results': [e.getDict() for e in es]})
        return result
