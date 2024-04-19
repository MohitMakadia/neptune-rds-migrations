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
    has_participant = Column(String(255))
    consists_of = Column(String(255))

    # chat_id  = Column(PGUUID(as_uuid=True))
    # has_participant = Column(PGUUID(as_uuid=True))
    # consists_of = Column(PGUUID(as_uuid=True))

    def tableLaunch():
        commitRds(deployTable(Base, engine))