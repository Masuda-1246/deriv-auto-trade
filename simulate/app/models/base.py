from contextlib import contextmanager
import logging
import threading

from sqlalchemy import Column, DateTime, Float, Integer
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

    @classmethod
    def get_tick(cls):
      with session_scope() as session:
        ticks = session.query(Tick).order_by(desc(cls.timestamp)).limit(1).all()
        ticks.reverse()
        if ticks is None:
          return []
        return ticks[0]

class Rating(Base):
    __tablename__ = 'ratings'
    timestamp = Column(DateTime, primary_key=True, nullable=False)
    limit = Column(Integer)
    total_rating = Column(Float)
    touch_limit = Column(Integer)
    touch_rating = Column(Float)
    notouch_limit = Column(Integer)
    notouch_rating = Column(Float)

    @classmethod
    def create(cls, timestamp, limit, total_rating, touch_limit, touch_rating, notouch_limit, notouch_rating):
      rating = Rating(timestamp=timestamp, limit=limit, total_rating=total_rating, touch_limit=touch_limit, touch_rating=touch_rating, notouch_limit=notouch_limit, notouch_rating=notouch_rating)
      try:
        with session_scope() as session:
            session.add(rating)
            return rating
      except IntegrityError:
        return False

    @classmethod
    def get_all_rating(cls, limit=100):
      with session_scope() as session:
        ratings = session.query(Tick).order_by(desc(cls.timestamp)).limit(limit).all()
        ratings.reverse()
        if ratings is None:
          return []
        return ratings


class Balance(Base):
    __tablename__ = 'balances'
    timestamp = Column(DateTime, primary_key=True, nullable=False)
    price = Column(Float)

    @classmethod
    def create(cls, timestamp, price):
      balance = Balance(timestamp=timestamp, price=price)
      try:
        with session_scope() as session:
            session.add(balance)
            return balance
      except IntegrityError:
        return False

    @classmethod
    def get_all_balance(cls, limit=100):
      with session_scope() as session:
        balances = session.query(Tick).order_by(desc(cls.timestamp)).limit(limit).all()
        balances.reverse()
        if balances is None:
          return []
        return balances

    @property
    def value(self):
      return {
        "timestamp":self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "price":self.price
      }

def initDB():
  Base.metadata.create_all(bind=engine)