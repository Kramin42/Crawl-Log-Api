from sqlalchemy import Column, Integer, Enum, Sequence, Text, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
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
    type = Column(Enum(EventType), nullable=False)
    data = Column(Text, nullable=False)
    time = Column(DateTime, nullable=False)
    src_abbr = Column(String(10), nullable=False)
    src_url = Column(String(1000), nullable=False)

    def __repr__(self):
        return "<Event(id={event.id}, type={event.type}, time={event.time}, src_abbr={event.src_abbr}, src_url={event.src_url}, data={event.data})>".format(event=self)

    def getDict(self):
        return {'type': self.type.value,
                'data': json.loads(self.data),
                'time': self.time.strftime('%s'),
                'src_abbr': self.src_abbr,
                'src_url': self.src_url}

class Logfile(Base):
    __tablename__ = 'logfile'
    path = Column(String(1000), primary_key=True)
    offset = Column(Integer, default=0, nullable=False)

    def __repr__(self):
        return "<Logfile(path={logfile.path}, offset={logfile.offset})>".format(logfile=self)

# End Object defs

engine = create_engine(SQLALCHEMY_DATABASE_URI)

session = sessionmaker(expire_on_commit=False, autocommit=False)
session.configure(bind=engine)
Base.metadata.create_all(engine)

def get_session():
    return session()
