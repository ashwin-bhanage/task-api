from fastapi import FastAPI, status, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db, User, Task
from app.models import UserCreate, UserResponse, TaskCreate, TaskResponse, TaskUpdate

app = FastAPI(title="Task Management API")

@app.get("/")
def root():
    return {"message": "Welcome to Task API."}

@app.post("/users", response_model=UserResponse, status_code= status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # 1. Check if email exists
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # 2. Create new user
    db_user = User(name = user.name, email = user.email)

    # 3. Add to database
    db.add(db_user)
    db.commit()
    db.refresh(db_user)  # Gets the ID and created_at from DB

    # 4. Return user
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

    # 2. Create new task
    db_task = Task(user_id = task.user_id, title = task.title, description = task.description, status = task.status)

    # 3. Add to database
    db.add(db_task)
    db.commit()
    db.refresh(db_task)  # Gets the ID and created_at from DB

    # 4. Return task
    return db_task


# List tasks
@app.get("/tasks", response_model=list[TaskResponse])
def list_tasks(user_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Task)
    if user_id is not None:
        query = query.filter(Task.user_id == user_id)
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

