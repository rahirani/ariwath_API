import status
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.crud import verify_otp_for_user
from app.schemas import OTPVerifyRequest,LoginForm
from app.auth import authenticate_user, create_access_token
from app import models, crud, database, schemas, utils, auth
from fastapi import BackgroundTasks
from jose import jwt, JWTError
from datetime import timedelta, datetime
ACCESS_TOKEN_EXPIRE_MINUTES = 30
from fastapi.responses import JSONResponse
from app.utils import send_welcome_email

SECRET_KEY = "airawath"  # Replace with a secure, random key
ALGORITHM = "HS256"
RESET_TOKEN_EXPIRE_MINUTES = 15  # Token validity

# Create all database tables
models.Base.metadata.create_all(bind=database.engine)  # Recreates tables with updated structure

# Initialize the FastAPI app
app = FastAPI()

# Dependency to get a database session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register/", response_model=schemas.UserResponse)
async def register_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    # Check if passwords match
    if user.password != user.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    # Check if the email is already registered
    if crud.get_user_by_email(db, email=user.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check if the phone number is already registered
    if crud.get_user_by_phone(db, phone_number=user.phone_number):
        raise HTTPException(status_code=400, detail="Phone number already registered")

    # Create the user in the database
    new_user = crud.create_user(db=db, user=user)

    # Generate OTP and send via email
    otp = utils.generate_otp()
    crud.set_otp_for_user(db, new_user, otp)
    try:
        await utils.send_otp_email(background_tasks, email=user.email, otp=otp)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send OTP: {str(e)}")

    return new_user


@app.post("/automated-questions/")
async def automated_questions(
        user_id: int,
        questions: schemas.AutomatedQuestions,
        db: Session = Depends(get_db)
):
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if not user.otp_verified:
        raise HTTPException(status_code=400, detail="OTP verification required.")

    updated_user = crud.save_automated_questions(db, user_id, questions)
    if not updated_user:
        raise HTTPException(status_code=400, detail="Failed to save responses.")
    return {"message": "Automated questions saved successfully. Proceed to profile building."}


# Route for updating user profile
@app.put("/update-profile/", response_model=schemas.UserResponse)
async def update_profile(request: schemas.UserProfileUpdate, db: Session = Depends(get_db)):
    updated_user = crud.update_user_profile(db, user_id=request.user_id, profile_data=request)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@app.post("/verify-otp/")
async def verify_otp(request: OTPVerifyRequest, db: Session = Depends(get_db)):
    # Fetch the user from the database
    user = crud.get_user_by_id(db, user_id=request.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Verify the OTP
    if not verify_otp_for_user(db, user, request.otp):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    return {"message": "OTP verified successfully"}

@app.post("/login", response_model=schemas.Token)
async def login_for_access_token(request: LoginForm, db: Session = Depends(get_db)):
    # Ensure both email and password are provided
    if not request.email:
        raise HTTPException(
            status_code=400,
            detail="Invalid email.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not request.password:
        raise HTTPException(
            status_code=400,
            detail="Password is required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Authenticate the user
    user = authenticate_user(db, email=request.email, password=request.password)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid credentials, please try again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if OTP is verified
    if not user.otp_verified:
        raise HTTPException(
            status_code=400,
            detail="OTP verification required. Please verify your OTP to log in.",
        )

    # Generate access token upon successful authentication
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    # Return a success message with the access token
    return JSONResponse(
        content={
            "message": "Login successful. Redirecting to dashboard...",
            "access_token": access_token,
            "token_type": "bearer"
        }
    )


# Function to generate password reset token
def create_reset_token(email: str):
    expire = datetime.utcnow() + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": email, "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Request Password Reset Endpoint
@app.post("/request-password-reset/")
async def request_password_reset(request: schemas.PasswordResetRequest, db: Session = Depends(get_db),
                                 background_tasks: BackgroundTasks = BackgroundTasks()):
    # Check if the user exists
    user = crud.get_user_by_email(db, email=request.email)
    if not user:
        raise HTTPException(status_code=404, detail="No account found with the provided Email.")

    # Generate reset token and send email
    token = create_reset_token(email=user.email)
    reset_link = f"http://example.com/reset-password?token={token}"

    # Send reset link via email
    try:
        await utils.send_reset_email(background_tasks, email=user.email, link=reset_link)
        print("token: ",token)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send reset link: {str(e)}")

    return {"message": "A reset link has been sent to your Email."}


# Confirm Password Reset Endpoint
@app.post("/confirm-password-reset/")
async def confirm_password_reset(request: schemas.PasswordResetConfirm, db: Session = Depends(get_db)):
    # Verify if passwords match
    if request.new_password != request.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match.")

    # Decode the token
    try:
        payload = jwt.decode(request.token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=400, detail="Invalid token.")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token.")

    # Fetch user from database
    user = crud.get_user_by_email(db, email=email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    # Update the user's password
    hashed_password = utils.hash_password(request.new_password)
    user.hashed_password = hashed_password
    db.commit()
    db.refresh(user)

    return {"message": "Your password has been reset successfully. Please log in with your new password."}

@app.post("/finalize-registration/")
async def finalize_registration(user_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    print(f"[DEBUG] Finalizing registration for user_id: {user_id}")
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if not user.otp_verified:
        raise HTTPException(status_code=400, detail="OTP verification required.")
    if user.registration_complete:
        return {"message": "Registration already completed."}

    # Finalize registration
    updated_user = crud.finalize_registration(db, user_id)
    if not updated_user:
        raise HTTPException(status_code=400, detail="Failed to finalize registration.")

    # Send welcome email
    await send_welcome_email(background_tasks, email=user.email, username=user.username)

    return {"message": "Thank you for registering! Welcome to Airawat!"}

