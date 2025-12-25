from fastapi import FastAPI, status, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db, User
from app.models import UserCreate, UserResponse

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
