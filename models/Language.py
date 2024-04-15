from sqlalchemy import Column, Integer, String, Boolean, Numeric , ForeignKey
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from utils.connect import rdsConnect
from sqlalchemy.orm import relationship
from utils.session import createRdsSession, commitRds

# from worker import Worker 

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
    # worker_id = Column(Integer, ForeignKey('Worker.worker_id')) 
    # customer_id = Column(Integer, ForeignKey('Customer.customer_id'))
    # customers = relationship('Customer', back_populates='language')
    # workers = relationship('Worker', back_populates='language')


    def tableLaunch():
        Base.metadata.create_all(engine)
        session = createRdsSession()
        commitRds(session)