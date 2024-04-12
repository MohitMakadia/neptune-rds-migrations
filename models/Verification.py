from sqlalchemy import Column, Integer, String, Boolean, Numeric , ForeignKey
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from utils.connect import rdsConnect
from utils.rdsSession import createRdsSession, commitRds
from sqlalchemy.orm import relationship


Base = declarative_base()
engine = rdsConnect()


class Verification(Base):
    __tablename__ = "Verification"

    id = Column(Integer, primary_key=True)
    used_to_verify_id= Column(PGUUID(as_uuid=True))
    last_login = Column(Integer)
    type_email = Column(String(1000))
    user_id = Column(PGUUID(as_uuid=True))
    #customer_id = Column(PGUUID(as_uuid=True), ForeignKey('Customer.customer_id'))
    # worker_id = Column(PGUUID(as_uuid=True), ForeignKey('Worker.worker_id'))
    # worker = relationship("Worker", back_populates="verifications")
    # customer = relationship("Customer", back_populates="verifications")



    def tableLaunch():
        Base.metadata.create_all(engine)
        session = createRdsSession()
        commitRds(session)