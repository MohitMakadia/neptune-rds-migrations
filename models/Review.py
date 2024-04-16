from sqlalchemy import Column, Integer, String, Boolean, Numeric , ForeignKey
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from utils.connect import rdsConnect
from sqlalchemy.orm import relationship
from utils.session import commitRds, deployTable
from sqlalchemy.ext.declarative import declarative_base 


# from worker import Worker 

Base = declarative_base()
engine = rdsConnect()




class Review(Base):
    __tablename__ = "Review"

    id = Column(Integer, primary_key=True)
    review_id  = Column(PGUUID(as_uuid=True))  #property id 
    score = Column(Integer())
    text = Column(String(1000))
    evaluated = Column(PGUUID(as_uuid=True))  #out vertex id consists of customer id 
    written_by = Column(PGUUID(as_uuid=True)) #out vertex id consists of worked id 

    def tableLaunch():
        commitRds(deployTable(Base, engine))