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




class Vertex(Base):
    __tablename__ = "Vertex"

    id = Column(Integer, primary_key=True)
    vertex_id  = Column(PGUUID(as_uuid=True))  #property id 
    last_login = Column(Integer())
    

    def tableLaunch():
        commitRds(deployTable(Base, engine))