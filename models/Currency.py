# type: ignore[import]
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from utils.connect import rdsConnect
from utils.session import commitRds, deployTable

Base = declarative_base()
engine = rdsConnect()

class Currency(Base):
    
    __tablename__ = "Currency"

    id = Column(Integer, primary_key=True)
    currency_id = Column(String(1000))
    code = Column(String(255))
    country = Column(String(255))
    last_login = Column(Integer())
    name = Column(String(255))
    is_currency_for = Column(String(1000))

    def tableLaunch():
        commitRds(deployTable(Base, engine))
