from sqlalchemy import Column, Integer, String, Boolean, Numeric
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from utils.connect import rdsConnect
from utils.rdsSession import createRdsSession, commitRds

Base = declarative_base()
engine = rdsConnect()

class Day(Base):
    __tablename__ = "Day"

    id = Column(Integer, primary_key=True)
    day_id  = Column(PGUUID(as_uuid=True))
    day_name = Column(String(1000))
    day_of_week = Column(Integer)
    last_login = Column(Integer)  # Assuming it's a nullable field

    def tableLaunch():
        Base.metadata.create_all(engine)
        session = createRdsSession()
        commitRds(session)