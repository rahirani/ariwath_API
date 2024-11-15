from sqlalchemy import DateTime
from sqlalchemy import Column, Integer, String, Boolean, Date, Text, Enum, Float, ForeignKey
from app.database import Base
import enum

class PronounsEnum(enum.Enum):
    he = "he"
    she = "she"
    they = "they"

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(20), unique=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    phone_number = Column(String(10), unique=True, nullable=False)
    otp_verified = Column(Boolean, default=False)
    otp = Column(String, nullable=True)  # Stores the OTP code
    otp_expiration = Column(DateTime, nullable=True)  # Stores OTP expiration time

    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    middle_name = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    location = Column(String, nullable=True)
    dob = Column(Date, nullable=True)
    pronouns = Column(Enum(PronounsEnum), nullable=True)

    # Level 1 profile information
    income = Column(String, nullable=True)
    education_level = Column(String, nullable=True)
    personal_income = Column(Float, nullable=True)

    # Level 2 additional information
    hobby = Column(String, nullable=True)
    favorite_team = Column(String, nullable=True)  # Conditional input based on hobby
    social_media_profiles = Column(Text, nullable=True)  # JSON or string for simplicity

    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<User(username={self.username}, email={self.email})>"

