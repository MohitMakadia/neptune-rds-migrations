from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from utils.connect import rdsConnect
from utils.session import commitRds, deployTable
import uuid

Base = declarative_base()
engine = rdsConnect()

class Payment(Base):
    
    __tablename__ = "Payment"

    id = Column(String(100), primary_key=True)
    created_at = Column(Integer())
    currency = Column(String(50))
    current_status = Column(String(50))
    last_login = Column(Integer())
    latitude = Column(Float())
    longitute = Column(Float())
    place_id = Column(String(200))
    updated_at = Column(Integer())
    value = Column(Integer())
    issued_by = Column(PGUUID(as_uuid=True))

    def tableLaunch():
        commitRds(deployTable(Base, engine))
