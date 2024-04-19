from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from utils.connect import rdsConnect
from utils.session import commitRds, deployTable

Base = declarative_base()
engine = rdsConnect()

class Message(Base):
    
    __tablename__ = "Message"

    id = Column(Integer, primary_key=True)
    message_id = Column(String(255))
    content = Column(String(1000))
    last_login = Column(Integer())
    seen = Column(Boolean, default=False)
    sent_timestamp = Column(Integer())
    authored_by = Column(String(255))
    addressed_to = Column(String(255))
    is_part_of = Column(String(255))

    # message_id = Column(PGUUID(as_uuid=True))
    # authored_by = Column(PGUUID(as_uuid=True))
    # addressed_to = Column(PGUUID(as_uuid=True))
    # is_part_of = Column(PGUUID(as_uuid=True))
    
    def tableLaunch():
        commitRds(deployTable(Base, engine))
