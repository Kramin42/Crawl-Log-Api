from calendar import timegm

from sqlalchemy import Column, Integer, Enum, Sequence, Text, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import enum
import json

SQLALCHEMY_DATABASE_URI = "sqlite:///pubsub.db"

Base = declarative_base()

class EventType(enum.Enum):
    game = 'game'
    milestone = 'milestone'

# Object defs

class Event(Base):
    __tablename__ = 'event'
    id = Column(Integer, primary_key=True)
    type = Column(Enum(EventType), nullable=False, index=True)
    data = Column(Text, nullable=False)
    time = Column(DateTime, nullable=False)
    src_abbr = Column(String(10), nullable=False)

    def __repr__(self):
        return "<Event(id={event.id}, type={event.type}, time={event.time}, src_abbr={event.src_abbr}, data={event.data})>".format(event=self)

    def getDict(self):
        return {'id': self.id,
                'type': self.type.value,
                'data': json.loads(self.data),
                'time': timegm(self.time.timetuple()),
                'src_abbr': self.src_abbr}

class Logfile(Base):
    __tablename__ = 'logfile'
    path = Column(String(1000), primary_key=True)
    offset = Column(Integer, default=0, nullable=False)

    def __repr__(self):
        return "<Logfile(path={logfile.path}, offset={logfile.offset})>".format(logfile=self)

# End Object defs

engine = create_engine(SQLALCHEMY_DATABASE_URI)

session_factory = sessionmaker(bind=engine, expire_on_commit=False, autocommit=False)
Base.metadata.create_all(engine)

@contextmanager
def get_session():
    Session = scoped_session(session_factory)
    yield Session()
    Session.remove()
