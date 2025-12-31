"""
Create models for UserData and UserResponse based on pydantic models
"""

from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import Literal

# Projects schemas
class ProjectCreate(BaseModel):
    name: str

    @field_validator("name")
    def name_not_empty(cls, value):
        if not value or not value.strip():
            raise ValueError("Project name cannot be empty")
        if len(value) > 100:
            raise ValueError("Project name cannot exceed 100 characters")
        return value.strip()


class ProjectResponse(BaseModel):
    id: int
    name: str
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True



class UserCreate(BaseModel):
    name: str
    email: EmailStr

    @field_validator("name")
    def name_not_empty(cls, value):
        if not value or not value.strip():
            raise ValueError("Name cannot be empty or whitespace only")
        return value.strip()

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

    class Config:
        # This tells Pydantic: "If you see a database object,
        # just grab the attributes like .id and .title
        from_attributes = True

"""
Task Create models -> userId, task, description, status(pending, completed, inprogress)
Note description is optional, and status is pending by default

Task Reponse models -> id, userID, title, description, status, created, updated
"""

class TaskCreate(BaseModel):
    user_id: int
    project_id: int
    title: str
    description: str | None = None
    status: Literal["pending", "completed", "in_progress"] = "pending"
    priority: Literal["Normal", "High", "Low"] = "Normal"
    due_date: datetime | None = None

    @field_validator("title")
    def title_length_validator(cls, value):
        if not value or not value.strip():
            raise ValueError("Title cannot be empty or whitespace only")
        if len(value) > 200:
            raise ValueError("Title cannot exceed 200 characters")
        return value.strip()


class TaskResponse(BaseModel):
    id: int
    user_id: int
    project_id: int
    title: str
    description: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime
    priority: str
    due_date: datetime | None = None

    class Config:
        from_attributes = True

# Taskdelete --> title, desc, status, fiell_valid for title
class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: Literal["pending", "completed", "in_progress"] | None = None
    priority: Literal["Normal", "High", "Low"] | None = None
    due_date: datetime | None = None

    @field_validator("title")
    def title_not_empty(cls, value):
        if value is not None:
            if not value.strip():
                raise ValueError("Title cannot be empty or whitespace only")
            if len(value) > 200:
                raise ValueError("Title cannot exceed 200 characters")
        return value
