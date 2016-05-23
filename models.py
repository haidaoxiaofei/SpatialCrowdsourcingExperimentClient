from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import db_config

__author__ = 'Jian Xun'

engine = create_engine('mysql://%s:%s@%s:%s/%s?charset=utf8' % (db_config.USERNAME,
                                                                db_config.PASSWORD,
                                                                db_config.HOST,
                                                                db_config.PORT,
                                                                db_config.DB),
                       encoding="utf-8", pool_recycle=7200, echo=False)

Base = declarative_base()
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()


class WorkerDetail(Base):
    __tablename__ = 'worker_detail'
    id = Column(Integer, primary_key=True)
    capacity = Column(Integer)
    reliability = Column(REAL())
    min_direction = Column(REAL())
    max_direction = Column(REAL())
    velocity = Column(REAL())
    region_min_lon = Column(REAL())
    region_min_lat = Column(REAL())
    region_max_lon = Column(REAL())
    region_max_lat = Column(REAL())
    longitude = Column(REAL())
    latitude = Column(REAL())
    is_online = Column(Integer, primary_key=True)
    # PrimaryKeyConstraint('id', 'is_online', name='wdt_pk')


class HitDetail(Base):
    __tablename__ = 'hit_detail'
    id = Column(Integer, primary_key=True)
    confidence = Column(REAL())
    entropy = Column(REAL())
    is_valid = Column(Integer)

    required_answer_count = Column(Integer, default=0)
    begin_time = Column(Integer, default=0)
    end_time = Column(Integer, default=0)

    longitude = Column(REAL())
    latitude = Column(REAL())
