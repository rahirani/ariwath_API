import random
import string
from passlib.context import CryptContext
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from fastapi import BackgroundTasks

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Corrected email configuration
conf = ConnectionConfig(
    MAIL_USERNAME="roshni hirani",
    MAIL_PASSWORD="fdmq pkwx bfbd igxj",
    MAIL_FROM="roshnihirani3499@gmail.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",  # e.g., "smtp.gmail.com"
    MAIL_STARTTLS=True,  # Enable STARTTLS
    MAIL_SSL_TLS=False,  # Set to True if using SSL/TLS encryption
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

# Function to hash passwords
def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)

# Function to verify passwords
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

# Add this code in utils.py
def generate_otp(length=6) -> str:
    """Generate a random numeric OTP of specified length."""
    return ''.join(random.choices(string.digits, k=length))

async def send_otp_email(background_tasks: BackgroundTasks, email: str, otp: str):
    """Send an OTP via email."""
    subject = "Your OTP Verification Code"
    body = f"Your OTP code is: {otp}"

    message = MessageSchema(
        subject=subject,
        recipients=[email],
        body=body,
        subtype="plain"
    )

    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message)

from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def send_reset_email(background_tasks: BackgroundTasks, email: str, link: str):
    """Send password reset email."""
    message = MessageSchema(
        subject="Password Reset Request",
        recipients=[email],
        body=f"Click the following link to reset your password: {link}",
        subtype="html"
    )
    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message)