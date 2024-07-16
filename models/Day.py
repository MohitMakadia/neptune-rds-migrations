# type: ignore[import]
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from utils.connect import rds_connect
from utils.session import commit_rds, deploy_table

Base = declarative_base()
engine = rds_connect()


class Day(Base):

    __tablename__ = "Day"

    id = Column(Integer, primary_key=True)
    day_id = Column(String(255))
    day_name = Column(String(15))
    day_of_week = Column(Integer())
    last_login = Column(Integer())
    is_available_for = Column(String(255))

    @staticmethod
    def table_launch():
        commit_rds(deploy_table(Base, engine))
