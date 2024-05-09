from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base 
from utils.connect import rdsConnect
from utils.session import commitRds, deployTable

Base = declarative_base()
engine = rdsConnect()

class Review(Base):
    
    __tablename__ = "Review"

    id = Column(Integer, primary_key=True)
    review_id  = Column(String(255))
    score = Column(Integer())
    text = Column(String(1000))
    author_id = Column(String(255))
    receiver_id = Column(String(255))
    customer_id = Column(String(255))
    worker_id = Column(String(255))

    def tableLaunch():
        commitRds(deployTable(Base, engine))