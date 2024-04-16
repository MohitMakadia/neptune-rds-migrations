from sqlalchemy import Column, Integer, String, Boolean, Numeric , ForeignKey
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from utils.connect import rdsConnect
from utils.session import createRdsSession, commitRds
from sqlalchemy.orm import relationship


Base = declarative_base()
engine = rdsConnect()


class VerificationCode(Base):
    __tablename__ = "VerificationCode"

    id = Column(Integer, primary_key=True)
    verificationcode_id = Column(String(200))
    active = Column(Boolean, default=False)
    created_timestamp = Column(Integer())
    person_id = Column(String(1000))    
    
    def tableLaunch():
        Base.metadata.create_all(engine)
        session = createRdsSession()
        commitRds(session)