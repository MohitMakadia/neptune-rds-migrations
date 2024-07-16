from utils.connect import rds_connect
from sqlalchemy import Column, Integer, String
from utils.session import commit_rds, deploy_table
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
engine = rds_connect()


class Dog(Base):
    __tablename__ = "Dog"

    id = Column(Integer, primary_key=True)
    dog_id = Column(String(255))
    blocks = Column(String(255))
    handling_required_by = Column(String(255))

    @staticmethod
    def table_launch():
        commit_rds(deploy_table(Base, engine))
