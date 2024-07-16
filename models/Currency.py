# type: ignore[import]
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from utils.connect import rds_connect
from utils.session import commit_rds, deploy_table

Base = declarative_base()
engine = rds_connect()


class Currency(Base):

    __tablename__ = "Currency"

    id = Column(Integer, primary_key=True)
    currency_id = Column(String(1000))
    code = Column(String(255))
    country = Column(String(255))
    last_login = Column(Integer())
    name = Column(String(255))
    is_currency_for = Column(String(1000))

    @staticmethod
    def table_launch():
        commit_rds(deploy_table(Base, engine))
