from utils.connect import rdsConnect
from sqlalchemy import Column, Integer, String
from utils.session import commitRds, deployTable
from sqlalchemy.ext.declarative import declarative_base 

Base = declarative_base()
engine = rdsConnect()

class User(Base):
    __tablename__ = "User"

    id = Column(Integer, primary_key=True)
    user_id  = Column(String(255))  
    favors = Column(String(255))

    def tableLaunch():
        commitRds(deployTable(Base, engine))