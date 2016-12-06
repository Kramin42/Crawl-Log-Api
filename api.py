import orm
import time
import logging
from orm import Event, EventType
from flask_restful import Resource, Api, reqparse

logger = logging.getLogger('api')

parser = reqparse.RequestParser()
parser.add_argument('offset', type=int)
parser.add_argument('limit', type=int)
parser.add_argument('type', type=EventType)

default_ok_result = {'status': 200, 'message': 'OK'}

class EventList(Resource):
    def get(self):
        t_i = time.time()
        offset = 0
        limit = 1000
        args = parser.parse_args()
        if args['offset']!=None: offset = args['offset']
        if args['limit']!=None and args['limit'] < 1000: limit = args['limit'] # TODO: make  max limit a config option
        with orm.get_session() as sess:
            q = sess.query(Event)
            if args['type']!=None: q = q.filter_by(type=args['type'])
            q = q.filter(Event.id >= offset)
            q = q.limit(limit)
            result = default_ok_result.copy()
            es = q.all()
            logger.debug('queried db in {} seconds.'.format(time.time()-t_i))
            result.update({'offset': offset, 'next_offset': (es[-1].id if len(es)>0 else offset), 'results': [e.getDict() for e in es]})
        logger.debug('done in {} seconds.'.format(time.time() - t_i))
        return result
