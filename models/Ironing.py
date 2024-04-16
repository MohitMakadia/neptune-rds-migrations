from utils.connect import rdsConnect
from sqlalchemy import Column, Integer
from utils.session import commitRds, deployTable
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.dialects.postgresql import UUID as PGUUID

Base = declarative_base()
engine = rdsConnect()

class Ironing(Base):
    __tablename__ = "Ironing"

    id = Column(Integer, primary_key=True)
    ironing_id  = Column(PGUUID(as_uuid=True))  
    blocks = Column(PGUUID(as_uuid=True))
    handling_required_by = Column(PGUUID(as_uuid=True))

    def tableLaunch():
        commitRds(deployTable(Base, engine))