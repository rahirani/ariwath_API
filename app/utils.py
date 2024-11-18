import random
import string
from passlib.context import CryptContext
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from fastapi import BackgroundTasks
import hashlib
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Existing configuration for email
conf = ConnectionConfig(
    MAIL_USERNAME="roshni.hirani@openxcell.com",
    MAIL_PASSWORD="uzpn onzg yojy kekv",
    MAIL_FROM="roshni.hirani@openxcell.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed_password: str) -> bool:
    return hash_password(password) == hashed_password

# Add this code in utils.py
def generate_otp(length=6) -> str:
    """Generate a random numeric OTP of specified length."""
    return ''.join(random.choices(string.digits, k=length))

async def send_otp_email(background_tasks: BackgroundTasks, email: str, otp: str):
    """
    Sends an OTP via email.
    :param background_tasks: FastAPI's background tasks for asynchronous execution.
    :param email: The recipient's email address.
    :param otp: The OTP code to send.
    """
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

async def send_welcome_email(background_tasks: BackgroundTasks, email: str, username: str):
    """
    Sends a welcome email to the user.
    """
    subject = "Welcome to Airawat!"
    body = f"""
    Hi {username},

    Thank you for registering with Airawat! We're excited to have you on board.

    Here are your account details:
    - Username: {username}
    - Email: {email}

    If you have any questions or need assistance, feel free to reach out.

    Welcome aboard!

    Best regards,
    The Airawat Team
    """
    message = MessageSchema(
        subject=subject,
        recipients=[email],
        body=body,
        subtype="plain"
    )

    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message)