# type: ignore[import]
from sqlalchemy.orm import sessionmaker 
from utils.connect import rdsConnect

def createRdsSession():
    engine = rdsConnect()
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

def commitRds(session):
    session.commit()
    session.close()
