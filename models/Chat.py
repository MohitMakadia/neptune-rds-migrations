from sqlalchemy import Column, Integer, Boolean, String
from sqlalchemy.ext.declarative import declarative_base 
from utils.connect import rdsConnect
from utils.session import commitRds, deployTable
from sqlalchemy.ext.declarative import declarative_base 

Base = declarative_base()
engine = rdsConnect()

class Chat(Base):

    __tablename__ = "Chat"

    id = Column(Integer, primary_key=True)
    chat_id  = Column(String(255))
    blocked = Column(Boolean, default=None)
    created_timestamp = Column(Integer())
    last_login = Column(Integer())
    worker_id = Column(String(255))
    customer_id = Column(String(255))
    message_id = Column(String(255))

    def tableLaunch():
        commitRds(deployTable(Base, engine))