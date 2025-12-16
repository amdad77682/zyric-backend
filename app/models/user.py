from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class User(BaseModel):
    """User model representing database user record"""
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
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
