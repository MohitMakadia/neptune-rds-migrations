# type: ignore[import]
from sqlalchemy import Column, Integer, String, Boolean, Numeric
from sqlalchemy.ext.declarative import declarative_base
from utils.connect import rdsConnect
from utils.session import createRdsSession, commitRds

Base = declarative_base()
engine = rdsConnect()


class Worker(Base):

    __tablename__ = "NewWorker"

    id = Column(Integer(), primary_key=True)
    worker_id = Column(String(255))
    amount = Column(Integer())
    domain_language = Column(String(1000))
    domain = Column(String(1000))
    email = Column(String(1000))
    experience = Column(Integer())
    first_name = Column(String(1000))
    internal_score = Column(Integer())
    is_online = Column(Boolean, default=False)
    is_suspended = Column(Boolean, default=False)
    # is_online = Column(Boolean)
    # is_suspended = Column(Boolean)
    is_deleted = Column(Boolean, default=False)
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
    # published = Column(Boolean)
    registered_date = Column(Integer())
    score = Column(Integer())
    user_alert = Column(Boolean, default=False)
    # user_alert = Column(Boolean)
    votes = Column(Integer())
    speaks = Column(String(100))
    verified_by = Column(String(100))
    wants_payment_in = Column(String(100))
    works_on = Column(String(100))
    participates_in = Column(String(100))
    receives = Column(String(100))
    favored_by = Column(String(100))
    authored = Column(String(100))
    wrote = Column(String(100))
    is_evaluated_by = Column(String(100))
    blocked_by = Column(String(100))
    issued = Column(String(100))
    favors = Column(String(100))
    wants_to_pay_in = Column(String(100))
    wants_service_on = Column(String(100))

    def tableLaunch():
        Base.metadata.create_all(engine)
        session = createRdsSession()
        commitRds(session)
