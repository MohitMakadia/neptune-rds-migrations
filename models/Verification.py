from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base 
from utils.connect import rdsConnect
from utils.session import createRdsSession, commitRds

Base = declarative_base()
engine = rdsConnect()

class Verification(Base):
    
    __tablename__ = "Verification"

    id = Column(Integer, primary_key=True)
    verification_id = Column(String(255)) 
    last_login = Column(Integer())
    type = Column(String(1000))
    used_to_verify = Column(String(255))
  
    def tableLaunch():
        Base.metadata.create_all(engine)
        session = createRdsSession()
        commitRds(session)