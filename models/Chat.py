from sqlalchemy import Column, Integer, Boolean, String
from sqlalchemy.ext.declarative import declarative_base
from utils.connect import rds_connect
from utils.session import commit_rds, deploy_table
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
engine = rds_connect()


class Chat(Base):

    __tablename__ = "Chat"

    id = Column(Integer, primary_key=True)
    chat_id = Column(String(255))
    blocked = Column(Boolean, default=None)
    created_timestamp = Column(Integer())
    last_login = Column(Integer())
    worker_id = Column(String(255))
    customer_id = Column(String(255))
    message_id = Column(String(255))

    @staticmethod
    def table_launch():
        commit_rds(deploy_table(Base, engine))
