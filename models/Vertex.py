from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from utils.connect import rds_connect
from utils.session import commit_rds, deploy_table
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
engine = rds_connect()


class Vertex(Base):

    __tablename__ = "Vertex"

    id = Column(Integer, primary_key=True)
    vertex_id = Column(PGUUID(as_uuid=True))
    last_login = Column(Integer())

    @staticmethod
    def table_launch():
        commit_rds(deploy_table(Base, engine))
