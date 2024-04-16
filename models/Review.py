from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from utils.connect import rdsConnect
from utils.session import commitRds, deployTable

Base = declarative_base()
engine = rdsConnect()

class Review(Base):
    
    __tablename__ = "Review"

    id = Column(Integer, primary_key=True)
    review_id  = Column(PGUUID(as_uuid=True))
    score = Column(Integer())
    text = Column(String(1000))
    evaluated = Column(PGUUID(as_uuid=True))
    written_by = Column(PGUUID(as_uuid=True))

    def tableLaunch():
        commitRds(deployTable(Base, engine))