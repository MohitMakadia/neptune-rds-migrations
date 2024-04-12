from sqlalchemy import Column, Integer, String, Boolean, Numeric , ForeignKey
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from utils.connect import rdsConnect
from utils.session import createRdsSession, commitRds
from sqlalchemy.orm import relationship


Base = declarative_base()
engine = rdsConnect()


class Verification(Base):
    __tablename__ = "Verification"

    id = Column(Integer, primary_key=True)
    verification_id = Column(PGUUID(as_uuid=True)) 
    last_login = Column(Integer)
    type = Column(String(1000))
    used_to_verify = Column(PGUUID(as_uuid=True))
  
    def tableLaunch():
        Base.metadata.create_all(engine)
        session = createRdsSession()
        commitRds(session)