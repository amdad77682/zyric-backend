from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field, field_validator


class UserRegisterRequest(BaseModel):
    """Schema for user registration request"""
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=8, max_length=72)
    role: Literal["teacher", "student"] = Field(..., description="User role: teacher or student")
    teacher_id: Optional[str] = Field(None, description="Required for students - UUID of the teacher")
    age: Optional[int] = Field(None, ge=0, le=150)
    gender: Optional[str] = Field(None, max_length=20)
    organization: Optional[str] = Field(None, max_length=255)
    profile_image: Optional[str] = None

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v


class UserLoginRequest(BaseModel):
    """Schema for user login request"""
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    """Schema for forgot password request"""
    email: EmailStr

class UserResponse(BaseModel):
    """Schema for user response (without sensitive data)"""
    id: str
    email: str
    first_name: str
    last_name: str
    role: str
    teacher_id: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    organization: Optional[str] = None
    profile_image: Optional[str] = None
    is_active: bool
    is_verified: bool
    is_verified: bool


class LoginResponse(BaseModel):
    """Schema for login response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class MessageResponse(BaseModel):
    """Schema for generic message response"""
    message: str
    success: bool = True
