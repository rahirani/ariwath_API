from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import date

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: EmailStr
    password: str = Field(..., min_length=8)
    confirm_password: str
    phone_number: str = Field(..., pattern="^\d{10}$")

    class Config:
        from_attributes = True
        orm_mode = True

class UserProfile(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    middle_name: Optional[str]
    age: Optional[int]
    location: Optional[str]
    dob: Optional[date]
    pronouns: Optional[str]

    class Config:
        from_attributes = True
        orm_mode = True

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    phone_number: str
    is_active: bool

    class Config:
        from_attributes = True

class LoginForm(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
class OTPVerifyRequest(BaseModel):
    user_id: int
    otp: str

class UserProfileUpdate(BaseModel):
    user_id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    age: Optional[int] = None
    location: Optional[str] = None
    dob: Optional[date] = None
    pronouns: Optional[str] = None

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, description="Password must be at least 8 characters long and include uppercase, lowercase, numeric, and special characters.")
    confirm_password: str

    @validator("new_password")
    def validate_password_complexity(cls, v):
        """Check that the password has uppercase, lowercase, digit, and special character."""
        if not any(c.islower() for c in v):
            raise ValueError("Password must include at least one lowercase letter.")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must include at least one uppercase letter.")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must include at least one digit.")
        if not any(c in "@$!%*?&" for c in v):
            raise ValueError("Password must include at least one special character: @$!%*?&")
        return v

    @validator("confirm_password")
    def passwords_match(cls, v, values):
        """Check that new_password and confirm_password match."""
        if "new_password" in values and v != values["new_password"]:
            raise ValueError("Passwords do not match.")
        return v