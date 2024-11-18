from sqlalchemy import DateTime
from sqlalchemy import Column, Integer, String, Boolean, Date, Text, Enum, Float, ForeignKey
from app.database import Base, engine
import enum

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, nullable=False)
    phone_number = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    otp = Column(String, nullable=True)  # Stores the OTP code
    otp_expiration = Column(DateTime, nullable=True)  # Stores OTP expiration time
    is_active = Column(Boolean, default=True)
    otp_verified = Column(Boolean, default=False)

    # Automated questions
    hobbies = Column(String, nullable=True)
    luxury_item = Column(String, nullable=True)
    preference = Column(String, nullable=True)
    tech_minimalist = Column(String, nullable=True)
    indoors_outdoors = Column(String, nullable=True)
    crayon_color = Column(String, nullable=True)

    # Profile fields
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    middle_name = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    location = Column(String, nullable=True)
    dob = Column(Date, nullable=True)
    pronouns = Column(String, nullable=True)  # Options: "he", "she", "they"

    registration_complete = Column(Boolean, default=False)  # registration_complete

# Create tables
Base.metadata.create_all(bind=engine)

