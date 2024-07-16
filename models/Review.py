from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from utils.connect import rds_connect
from utils.session import commit_rds, deploy_table

Base = declarative_base()
engine = rds_connect()


class Review(Base):

    __tablename__ = "Review"

    id = Column(Integer, primary_key=True)
    review_id = Column(String(255))
    score = Column(Integer())
    text = Column(String(1000))
    author_id = Column(String(255))
    receiver_id = Column(String(255))
    customer_id = Column(String(255))
    worker_id = Column(String(255))

    @staticmethod
    def table_launch():
        commit_rds(deploy_table(Base, engine))
