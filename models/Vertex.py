from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from utils.connect import rdsConnect
from utils.session import commitRds, deployTable
from sqlalchemy.ext.declarative import declarative_base 

Base = declarative_base()
engine = rdsConnect()

class Vertex(Base):
   
    __tablename__ = "Vertex"

    id = Column(Integer, primary_key=True)
    vertex_id  = Column(PGUUID(as_uuid=True))
    last_login = Column(Integer())
    
    def tableLaunch():
        commitRds(deployTable(Base, engine))