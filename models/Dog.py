from utils.connect import rdsConnect
from sqlalchemy import Column, Integer, String
from utils.session import commitRds, deployTable
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.dialects.postgresql import UUID as PGUUID

Base = declarative_base()
engine = rdsConnect()

class Dog(Base):
    __tablename__ = "Dog"

    id = Column(Integer, primary_key=True)
    dog_id  = Column(String(255))  
    blocks = Column(String(255))
    handling_required_by = Column(String(255))
    # dog_id  = Column(PGUUID(as_uuid=True))  
    # blocks = Column(PGUUID(as_uuid=True))
    # handling_required_by = Column(PGUUID(as_uuid=True))

    def tableLaunch():
        commitRds(deployTable(Base, engine))