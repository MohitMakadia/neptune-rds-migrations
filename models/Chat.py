from sqlalchemy import Column, Integer, String, Boolean, Numeric , ForeignKey
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from utils.connect import rdsConnect
from utils.session import createRdsSession, commitRds, deployRds
from sqlalchemy.orm import relationship
from utils.session import commitRds, deployTable


# from worker import Worker 

Base = declarative_base()
engine = rdsConnect()


Base = declarative_base()
engine = rdsConnect()

class Chat(Base):
    __tablename__ = "Chat"

    id = Column(Integer, primary_key=True)
    chat_id  = Column(PGUUID(as_uuid=True))  #property id 
    blocked = Column(Boolean, default=False)
    created_timestamp = Column(Integer)
    last_login = Column(Integer) 
    has_participant = Column(PGUUID(as_uuid=True))  #out vertex id 
    consists_of = Column(PGUUID(as_uuid=True))

    def tableLaunch():
        commitRds(deployTable(Base, engine))