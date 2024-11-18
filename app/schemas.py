from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import date

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: EmailStr
    phone_number: str = Field(..., pattern=r"^\d{10}$")
    password: str = Field(..., min_length=8)
    confirm_password: str

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
    email: str
    phone_number: str

    class Config:
        orm_mode = True

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
    first_name: Optional[str]
    last_name: Optional[str]
    middle_name: Optional[str] = None
    age: Optional[int]
    location: Optional[str]
    dob: Optional[date]
    pronouns: Optional[str]  # Options: "he", "she", "they"

    class Config:
        orm_mode = True

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

class AutomatedQuestions(BaseModel):
    hobbies: str = Field(..., description="What do you enjoy doing in your free time?")
    luxury_item: str = Field(..., description="If you could treat yourself to one luxury item, what would it be?")
    preference: str = Field(..., description="Are you more into experiences or physical gifts?")
    tech_minimalist: str = Field(..., description="Do you like tech gadgets or are you more of a minimalist?")
    indoors_outdoors: str = Field(..., description="Do you prefer spending time indoors or outdoors?")
    crayon_color: str = Field(..., description="If you were a crayon, what color would you be and why?")

