from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from utils.connect import rds_connect
from utils.session import commit_rds, deploy_table

Base = declarative_base()
engine = rds_connect()


class Message(Base):

    __tablename__ = "Message"

    id = Column(Integer, primary_key=True)
    message_id = Column(String(255))
    content = Column(String(100000))
    last_login = Column(Integer())
    seen = Column(Boolean, default=False)
    sent_timestamp = Column(Integer())
    author_id = Column(String(255))
    receiver_id = Column(String(255))
    customer_id = Column(String(255))
    worker_id = Column(String(255))
    chat_id = Column(String(255))

    @staticmethod
    def table_launch():
        commit_rds(deploy_table(Base, engine))
