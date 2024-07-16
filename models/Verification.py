from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from utils.connect import rds_connect
from utils.session import create_rds_session, commit_rds

Base = declarative_base()
engine = rds_connect()


class Verification(Base):

    __tablename__ = "Verification"

    id = Column(Integer, primary_key=True)
    verification_id = Column(String(255))
    last_login = Column(Integer())
    type = Column(String(1000))
    used_to_verify = Column(String(255))

    @staticmethod
    def table_launch():
        Base.metadata.create_all(engine)
        session = create_rds_session()
        commit_rds(session)
