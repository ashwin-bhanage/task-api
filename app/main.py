import os
from fastapi import FastAPI, status, HTTPException, Depends, Response
from sqlalchemy.orm import Session
from app.database import get_db, User, Task, Project
from app.models import UserCreate, UserResponse, TaskCreate, TaskResponse, TaskUpdate, ProjectCreate, ProjectResponse
from typing import Literal
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
# for the Error handling
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv

load_dotenv()

# from auth and token authentication
from app.auth import get_current_user
from app.security import get_password_hash, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.models import UserProfile, UserLogin, UserRegister, Token

# Entry point
app = FastAPI(
    title="Task Management API",
    description="Multi-user task management system with RESTful endpoints",
    version="2.0.0"
)

# Get frontend URL from environment
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# CORS for backend to frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Local development
        "https://ergo-task-board.vercel.app",  # Production frontend - UPDATE THIS
        "https://*.vercel.app"  # Allow all Vercel preview deployments
    ],  # FIXED
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========= auth routes ===========
@app.post("/auth/register", response_model=UserProfile, status_code= status.HTTP_201_CREATED)
def register_user(user: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException (
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )

    # create user with hash password
    hashed_password = get_password_hash(user.password)
    new_user = User(
        name = user.name,
        email = user.email,
        password_hash = hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@app.post("/auth/login")
def login(response: Response, crendentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == crendentials.email).first()

    if not user or not verify_password(crendentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )


    # create access token
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    # set HTTP-only cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False
    )

    return {
        "message": "Login successful",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }

@app.post("/auth/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Logout successful"}


@app.get("/auth/me", response_model= UserProfile)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get the authenticated user's profile"""
    return current_user


@app.get("/")
def root():
    return {"message": "Welcome to Task API."}

@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ADD THIS - requires auth
):
    """Create a new user (requires authentication)"""
    # Check if email exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password
    hashed_password = get_password_hash(user.password)

    db_user = User(
        name=user.name,
        email=user.email,
        password_hash=hashed_password
    )

    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")

    return db_user


# Get all users
@app.get("/users", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

# Get user by user_id
@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Post the task
@app.post("/tasks", response_model=TaskResponse, status_code= status.HTTP_201_CREATED)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    # 1. Check if user exists
    user = db.query(User).filter(User.id == task.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if task is ther in project
    project = db.query(Project).filter(Project.id == task.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # 2. Create new task
    db_task = Task(
        user_id = task.user_id,
        project_id = task.project_id,
        title = task.title,
        description = task.description,
        status = task.status,
        priority = task.priority,
        due_date = task.due_date
        )

    # 3. Add to database
    db.add(db_task)
    db.commit()
    db.refresh(db_task)  # Gets the ID and created_at from DB

    # 4. Return task
    return db_task


# List tasks
@app.get("/tasks", response_model=list[TaskResponse])
def list_tasks(
    user_id: int | None = None,
    project_id: int | None = None,
    status: Literal["pending", "completed", "in_progress"] | None = None,
    # priority: Literal["Normal", "High", "Low"] | None = None,
    db: Session = Depends(get_db)
    ):
    query = db.query(Task)
    if user_id is not None:
        query = query.filter(Task.user_id == user_id)

    if project_id is not None:
        query = query.filter(Task.project_id == project_id)

    if status is not None:
        query = query.filter(Task.status == status)

    # if priority is not None:
    #     query = query.filter(Task.priority == priority)

    tasks = query.all()
    return tasks

# Get the task by id
@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# Update the task
@app.patch("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    # 1. Check if task exist
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # 2. Update task
    update_data = task_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    # 3. Add to database
    db.commit()
    db.refresh(task)  # Gets the ID and created_at from DB

    # 4. Return task
    return task

# To delete a task
@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return

# Delete user
@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return


# Create project
@app.post("/projects", response_model=ProjectResponse, status_code= status.HTTP_201_CREATED)
def create_project(project: ProjectCreate, user_id: int, db: Session = Depends(get_db)):
    # 1. Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2. Create new project
    db_project = Project(name = project.name, created_by = user_id)

    # 3. Add to database
    db.add(db_project)
    db.commit()
    db.refresh(db_project)  # Gets the ID and created_at from DB

    # 4. Return project
    return db_project

# get project by id
@app.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

# list all projects
@app.get("/projects", response_model=list[ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    return projects

# delete the projects
@app.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return
