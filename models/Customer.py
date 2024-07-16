# type: ignore[import]
from sqlalchemy import Column, Integer, String, Boolean, Numeric
from sqlalchemy.ext.declarative import declarative_base
from utils.connect import rds_connect
from utils.session import create_rds_session, commit_rds

Base = declarative_base()
engine = rds_connect()


class Customer(Base):

    __tablename__ = "Customer1"

    id = Column(String(255), primary_key=True)
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
    personal_note = Column(String(10000))
    phone_no = Column(String(1000))
    profile_picture = Column(String(1000))
    published = Column(Boolean, default=False)
    registered_date = Column(Integer())
    score = Column(Integer())
    user_alert = Column(Boolean, default=False)
    votes = Column(Integer())
    max_distance = Column(Integer())
    location_address = Column(String(1000))
    location_city = Column(String(1000))
    location_country = Column(String(1000))
    location_place_id = Column(String(2000))
    location_slug = Column(String(1000))
    location_country_code = Column(String(10))
    location_longitude = Column(Numeric(precision=10, scale=6))
    location_latitude = Column(Numeric(precision=10, scale=6))

    @staticmethod
    def table_launch():
        Base.metadata.create_all(engine)
        session = create_rds_session()
        commit_rds(session)
