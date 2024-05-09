# type: ignore[import]
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base 
from utils.connect import rdsConnect
from utils.session import commitRds, deployTable

Base = declarative_base()
engine = rdsConnect()

class Day(Base):
    
    __tablename__ = "Day"

    id = Column(Integer, primary_key=True)
    day_id = Column(String(255))
    day_name = Column(String(15))
    day_of_week = Column(Integer())
    last_login = Column(Integer())
    is_working_day_for = Column(String(255))

    def tableLaunch():
        commitRds(deployTable(Base, engine))
