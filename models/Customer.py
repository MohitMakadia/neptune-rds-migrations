# type: ignore[import]
from sqlalchemy import Column, Integer, String, Boolean, Numeric
from sqlalchemy.ext.declarative import declarative_base
from utils.connect import rdsConnect
from utils.session import createRdsSession, commitRds

Base = declarative_base()
engine = rdsConnect()


class Customer(Base):

    __tablename__ = "NewCustomer"

    id = Column(Integer(), primary_key=True)
    customer_id = Column(String(255))
    amount = Column(Integer())
    domain_language = Column(String(1000))
    domain = Column(String(1000))
    duration = Column(Integer())
    email = Column(String(1000))
    experience = Column(Integer())
    first_name = Column(String(1000))
    internal_score = Column(Integer())
    interval = Column(Integer())
    is_deleted = Column(Boolean, default=False)
    is_online = Column(Boolean, default=False)
    is_suspended = Column(Boolean, default=False)
    last_login = Column(Integer())
    location_address = Column(String(1000))
    location_city = Column(String(1000))
    location_country = Column(String(1000))
    location_place_id = Column(String(2000))
    location_slug = Column(String(1000))
    personal_note = Column(String(10000))
    phone_no = Column(String(1000))
    profile_picture = Column(String(1000))
    published = Column(Boolean, default=False)
    registered_date = Column(Integer())
    score = Column(Integer())
    user_alert = Column(Boolean, default=False)
    votes = Column(Integer())
    location_longitude = Column(Numeric(precision=10, scale=6))
    location_latitude = Column(Numeric(precision=10, scale=6))
    max_distance = Column(Integer())
    verified_by = Column(String(1000))
    participates_in = Column(String(1000))
    authored = Column(String(1000))
    speaks = Column(String(1000))
    wants_to_pay_in = Column(String(1000))
    wants_service_on = Column(String(1000))
    favored_by = Column(String(1000))
    receives = Column(String(1000))
    issued = Column(String(1000))
    favors = Column(String(1000))
    is_evaluated_by = Column(String(1000))
    wrote = Column(String(1000))
    wants_payment_in = Column(String(1000))
    works_on = Column(String(1000))
    requires_handling = Column(String(1000))

    def tableLaunch():
        Base.metadata.create_all(engine)
        session = createRdsSession()
        commitRds(session)
