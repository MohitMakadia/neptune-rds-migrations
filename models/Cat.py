from utils.connect import rdsConnect
from sqlalchemy import Column, Integer, String
from utils.session import commitRds, deployTable
from sqlalchemy.ext.declarative import declarative_base 

Base = declarative_base()
engine = rdsConnect()

class Cat(Base):
    __tablename__ = "Cat"

    id = Column(Integer, primary_key=True)
    cat_id  = Column(String(255))  
    blocks = Column(String(255))
    handling_required_by = Column(String(255))

    def tableLaunch():
        commitRds(deployTable(Base, engine))