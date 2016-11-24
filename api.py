import orm
import logging
from orm import Event, EventType
from flask_restful import Resource, Api, reqparse

parser = reqparse.RequestParser()
parser.add_argument('offset', type=int)
parser.add_argument('limit', type=int)
parser.add_argument('type', type=EventType)

default_ok_result = {'status': 200, 'message': 'OK'}

class EventList(Resource):
    def get(self):
        offset = 0
        limit = 1000
        args = parser.parse_args()
        if args['offset']!=None: offset = args['offset']
        if args['limit']!=None and args['limit'] < 1000: limit = args['limit'] # TODO: make  max limit a config option
        sess = orm.get_session()
        q = sess.query(Event)
        if args['type']!=None: q = q.filter_by(type=args['type'])
        q = q.offset(offset).limit(limit)
        result = default_ok_result.copy()
        result.update({'offset': offset, 'count': q.count(), 'results': [e.getDict() for e in q.all()]})
        return result
