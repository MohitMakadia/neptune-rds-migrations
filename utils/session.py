# type: ignore[import]
from sqlalchemy.orm import sessionmaker
from utils.connect import rds_connect


def create_rds_session():
    engine = rds_connect()
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def commit_rds(session):
    session.commit()
    session.close()


def deploy_table(Base, engine):
    Base.metadata.create_all(engine)
    return create_rds_session()
