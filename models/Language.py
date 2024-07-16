from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from utils.connect import rds_connect
from utils.session import create_rds_session, commit_rds

Base = declarative_base()
engine = rds_connect()


class Language(Base):

    __tablename__ = "Language"

    id = Column(Integer, primary_key=True)
    language_id = Column(String(255))
    code = Column(String)
    last_login = Column(Integer())
    name = Column(String)
    spoken_by = Column(String(255))

    @staticmethod
    def table_launch():
        Base.metadata.create_all(engine)
        session = create_rds_session()
        commit_rds(session)
