from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from utils.connect import rdsConnect
from utils.session import createRdsSession, commitRds

Base = declarative_base()
engine = rdsConnect()

class Language(Base):

    __tablename__ = 'Language'

    id = Column(Integer, primary_key=True)
    language_id = Column(PGUUID(as_uuid=True))
    code = Column(String)
    last_login = Column(Integer())
    name = Column(String) 
    spoken_by = Column(PGUUID(as_uuid=True)) 

    def tableLaunch():
        Base.metadata.create_all(engine)
        session = createRdsSession()
        commitRds(session)