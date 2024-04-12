# type: ignore[import]
from sqlalchemy import Column, Integer, String, Boolean, Numeric
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from utils.connect import rdsConnect
from utils.rdsSession import createRdsSession, commitRds

Base = declarative_base()
engine = rdsConnect()

class Worker(Base):
    
    __tablename__ = "Worker"

    id = Column(Integer, primary_key=True)
    worker_id = Column(PGUUID(as_uuid=True))
    amount = Column(Integer())
    domain_language = Column(String(1000))
    domain = Column(String(1000))
    email = Column(String(1000))
    experience = Column(Integer())
    first_name = Column(String(1000))
    internal_score = Column(Integer())
    is_online = Column(Boolean, default=False)
    is_suspended = Column(Boolean, default=False)
    last_login = Column(Integer())
    location_address = Column(String(1000))
    location_city = Column(String(1000))
    location_country = Column(String(1000))
    location_longitude = Column(Numeric(precision=10, scale=6))
    location_latitude = Column(Numeric(precision=10, scale=6))
    location_place_id = Column(String(2000))
    location_slug = Column(String(1000))
    max_distance = Column(Integer())
    personal_note = Column(String(10000))
    profile_picture = Column(String(1000))
    published = Column(Boolean, default=False)
    registered_date = Column(Integer())
    score = Column(Integer())
    user_alert = Column(Boolean, default=False)
    votes = Column(Integer())


    #verified_by = Column(PGUUID(as_uuid=True), ForeignKey('Verification.used_to_verify_id'))
    #verifications = relationship("Verification",  back_populates="workers")


    def tableLaunch():
        Base.metadata.create_all(engine)
        session = createRdsSession()
        commitRds(session)
