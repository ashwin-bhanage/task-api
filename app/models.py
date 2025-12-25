"""
Create models for UserData and UserResponse based on pydantic models
"""

from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: EmailStr

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

    class Config:
        # Helps to allow conversion from SQLAlchemy model
        from_attritubes = True
