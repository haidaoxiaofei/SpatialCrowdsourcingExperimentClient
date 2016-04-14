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


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255))  # encrypt later
    credit = Column(Integer, default=0)
    active = Column(Boolean(), default=False)
    created_on = Column(DateTime, default=datetime.datetime.now)
    iat = Column(Integer, default=0)


class WorkerDetail(Base):
    __tablename__ = 'worker_detail'
    id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    capacity = Column(Integer)
    reliability = Column(REAL())
    min_direction = Column(REAL())
    max_direction = Column(REAL())
    velocity = Column(REAL())
    region_min_lon = Column(REAL())
    region_min_lat = Column(REAL())
    region_max_lon = Column(REAL())
    region_max_lat = Column(REAL())
    is_online = Column(BOOLEAN, default=False)


class HitDetail(Base):
    __tablename__ = 'hit_detail'
    id = Column(Integer, ForeignKey('hit.id'), primary_key=True)
    confidence = Column(REAL())
    entropy = Column(REAL())
    is_valid = Column(BOOLEAN, default=True)


class HIT(Base):
    __tablename__ = 'hit'
    id = Column(Integer, primary_key=True)
    type = Column(String(20))
    title = Column(String(500))
    description = Column(TEXT)

    attachment_id = Column(Integer, ForeignKey('attachment.id'))

    campaign_id = Column(Integer, ForeignKey('campaign.id'))

    credit = Column(Integer, default=10)
    status = Column(String(20), default='open')  # or closed
    required_answer_count = Column(Integer, default=3)
    min_selection_count = Column(Integer, default=1)
    max_selection_count = Column(Integer, default=1)
    begin_time = Column(DateTime, default=datetime.datetime.now)
    end_time = Column(DateTime, default=lambda: datetime.datetime.now() + datetime.timedelta(days=1))
    created_on = Column(DateTime, default=datetime.datetime.now)

    location_id = Column(Integer, ForeignKey('location.id'), nullable=True)

    requester_id = Column(Integer, ForeignKey('user.id'))


class UserLastPosition(Base):
    __tablename__ = 'user_last_position'
    id = Column(Integer, primary_key=True)

    longitude = Column(REAL())
    latitude = Column(REAL())
    z = Column(Integer)  # meter?

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    last_updated = Column(DateTime, onupdate=datetime.datetime.now)


class Message(Base):
    __tablename__ = 'message'
    id = Column(Integer, primary_key=True)
    type = Column(String(50), nullable=False)
    content = Column(String(300), nullable=False)

    att_type = Column(String(20))
    attachment = Column(String(200))

    sender_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    receiver_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    status = Column(String(20), default='new', nullable=False)  # delivered, read

    created_on = Column(DateTime, default=datetime.datetime.now, nullable=False)
