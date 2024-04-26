from sqlalchemy import Column, Integer, Boolean, String
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from utils.connect import rdsConnect
from sqlalchemy.orm import relationship
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

    # has_participant_worker = Column(String(255))
    # has_participant_customer = Column(String(255))
    # consists_of = Column(String(255))

    def tableLaunch():
        commitRds(deployTable(Base, engine))