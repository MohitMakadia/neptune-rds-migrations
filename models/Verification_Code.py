from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from utils.connect import rds_connect
from utils.session import create_rds_session, commit_rds

Base = declarative_base()
engine = rds_connect()


class VerificationCode(Base):

    __tablename__ = "VerificationCode"

    id = Column(Integer, primary_key=True)
    verificationcode_id = Column(String(200))
    active = Column(Boolean, default=False)
    created_timestamp = Column(Integer())
    person_id = Column(String(1000))

    @staticmethod
    def table_launch():
        Base.metadata.create_all(engine)
        session = create_rds_session()
        commit_rds(session)
