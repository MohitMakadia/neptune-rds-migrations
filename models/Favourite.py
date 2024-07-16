from utils.connect import rds_connect
from sqlalchemy import Column, Integer, String
from utils.session import commit_rds, deploy_table
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
engine = rds_connect()


class Favourite(Base):
    __tablename__ = "Favourite"

    id = Column(Integer, primary_key=True)
    person_id = Column(String(255))
    favors = Column(String(255))
    favored_by = Column(String(255))

    @staticmethod
    def table_launch():
        commit_rds(deploy_table(Base, engine))
