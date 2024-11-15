from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app import models, schemas, utils


# Function to get a user by email
def get_user_by_email(db: Session, email: str):
    """Fetch a user from the database using their email."""
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    """Fetch a user from the database using their ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()

# Function to get a user by phone number
def get_user_by_phone(db: Session, phone_number: str):
    """Fetch a user from the database using their phone number."""
    return db.query(models.User).filter(models.User.phone_number == phone_number).first()

# Function to create a new user
def create_user(db: Session, user: schemas.UserCreate):
    """Create a new user in the database."""
    hashed_password = utils.hash_password(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        phone_number=user.phone_number
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# Function to update user profile information
def update_user_profile(db: Session, user_id: int, profile_data: schemas.UserProfile):
    """Update basic profile information of an existing user."""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db_user.first_name = profile_data.first_name or db_user.first_name
        db_user.last_name = profile_data.last_name or db_user.last_name
        db_user.middle_name = profile_data.middle_name or db_user.middle_name
        db_user.age = profile_data.age or db_user.age
        db_user.location = profile_data.location or db_user.location
        db_user.dob = profile_data.dob or db_user.dob
        db_user.pronouns = profile_data.pronouns or db_user.pronouns

        db.commit()
        db.refresh(db_user)
    return db_user


def set_otp_for_user(db: Session, user: models.User, otp: str):
    """Set OTP and expiration time for the user."""
    user.otp = otp
    user.otp_expiration = datetime.now() + timedelta(minutes=5)
    db.commit()
    db.refresh(user)
    print(f"OTP set for user {user.id}: {user.otp} (expires at {user.otp_expiration})")
    return user

def verify_otp_for_user(db: Session, user: models.User, otp: str) -> bool:
    """Verify the OTP, ensuring it hasn't expired."""
    if user.otp == otp and user.otp_expiration > datetime.now():
        user.otp_verified = True
        user.otp = None  # Clear OTP after successful verification
        user.otp_expiration = None
        db.commit()
        db.refresh(user)
        return True
    return False
