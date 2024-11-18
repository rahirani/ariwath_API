from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app import models, schemas, utils


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_phone(db: Session, phone_number: str):
    return db.query(models.User).filter(models.User.phone_number == phone_number).first()

def save_automated_questions(db: Session, user_id: int, questions: schemas.AutomatedQuestions):
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    user.hobbies = questions.hobbies
    user.luxury_item = questions.luxury_item
    user.preference = questions.preference
    user.tech_minimalist = questions.tech_minimalist
    user.indoors_outdoors = questions.indoors_outdoors
    user.crayon_color = questions.crayon_color
    db.commit()
    db.refresh(user)
    return user


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = utils.hash_password(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        phone_number=user.phone_number,
        hashed_password=hashed_password,
        otp=None,
        otp_expiration=None,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_id(db: Session, user_id: int):
    """Fetch a user from the database using their ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()

def update_user_profile(db: Session, user_id: int, profile_data: schemas.UserProfileUpdate):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        return None

    # Update fields only if provided
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

def finalize_registration(db: Session, user_id: int):
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    user.registration_complete = True
    user.is_active = True
    db.commit()
    db.refresh(user)
    return user

