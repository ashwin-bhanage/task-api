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
