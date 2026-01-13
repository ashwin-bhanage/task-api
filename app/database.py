"""
Created the Database structure and works for creation of tables for the database.
"""
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text
from datetime import datetime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

db_url = "sqlite:///./tasks.db"

engine = create_engine(db_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class User(Base):
    """
    SQLAlchemy model for users table
    """
    # Tablename
    __tablename__ = "users"

    # Columns
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    tasks = relationship("Task", back_populates="owner")
    projects = relationship("Project", back_populates="creator")

# Add Project class including the tablename as 'projects' and attributes
# id, name created_by, created_at, with relationships to User as creator and Task as tasks
class Project(Base):
    """
    SQLAlchemy model for projects table
    """
    # Tablename
    __tablename__ = "projects"

    # Columns
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    creator = relationship("User", back_populates="projects")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")


class Task(Base):
    """
    SQLAlchemy model for tasks table
    """
    # Tablename
    __tablename__ = "tasks"

    # Columns
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # attributes added for the projects and owner as creator
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable = False)
    priority = Column(String, default="Normal") # "Low", "Normal", "High"
    due_date = Column(DateTime)

    # Relationships
    project = relationship("Project", back_populates="tasks")
    owner = relationship("User", back_populates="tasks")

def create_tables():
    Base.metadata.create_all(bind=engine)
