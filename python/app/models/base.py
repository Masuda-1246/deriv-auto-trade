from contextlib import contextmanager
import logging
import threading

from sqlalchemy import Column, DateTime, Float
from sqlalchemy import desc
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

import settings

logger = logging.getLogger(__name__)
Base = declarative_base()
engine = create_engine(f"sqlite:///{settings.db_name}?check_same_thread=False")
Session = scoped_session(sessionmaker(bind=engine))
lock = threading.Lock()

@contextmanager
def session_scope():
  session = Session()
  session.expire_on_commit = False
  try:
    lock.acquire()
    yield session
    session.commit()
  except Exception as e:
    session.rollback()
    logger.exception(f"session_scope error: {e}")
    raise
  finally:
    # session.close()
    session.expire_on_commit = True
    lock.release()

class Tick(Base):
    __tablename__ = 'ticks'
    timestamp = Column(DateTime, primary_key=True, nullable=False)
    price = Column(Float)

    @classmethod
    def create(cls, timestamp, ask, bid):
      price = (ask + bid) / 2
      tick = Tick(timestamp=timestamp, price=price)
      try:
        with session_scope() as session:
            session.add(tick)
            return tick
      except IntegrityError:
        return False

    @classmethod
    def get_all_ticks(cls, limit=100):
      with session_scope() as session:
        ticks = session.query(Tick).order_by(desc(cls.timestamp)).limit(limit).all()
        ticks.reverse()
        if ticks is None:
          return []
        return ticks

    @property
    def value(self):
      return {
        "timestamp":self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "price":self.price
      }

class DataFrameCandle(object):
    def __init__(self):
        self.ticks = []

    def set_all_ticks(self, limit=100):
        self.ticks = Tick.get_all_ticks(limit)
        return self.ticks

    @property
    def value(self):
      return {
        "data":[c.value for c in self.ticks]
      }

def initDB():
  Base.metadata.create_all(bind=engine)