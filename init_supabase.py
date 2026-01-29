from app.database import Base, engine, SessionLocal
from app.database import User, Project, Task
from app.security import get_password_hash
from datetime import datetime, timedelta, timezone

def init_database():
    """Initialize database with tables and demo data"""
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created!")

    # Create demo user
    db = SessionLocal()
    try:
        # Check if demo user exists
        existing = db.query(User).filter(User.email == "demo@example.com").first()
        if existing:
            print("ℹ️  Demo user already exists")
            return

        demo_user = User(
            name="Demo User",
            email="demo@example.com",
            password_hash=get_password_hash("password123")
        )
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)
        print(f"✅ Created demo user: {demo_user.email}")

        # Create demo project
        demo_project = Project(
            name="Demo Project",
            created_by=demo_user.id
        )
        db.add(demo_project)
        db.commit()
        db.refresh(demo_project)
        print(f"✅ Created demo project: {demo_project.name}")

        # Create demo task
        demo_task = Task(
            user_id=demo_user.id,
            project_id=demo_project.id,
            title="Welcome to TaskBoard!",
            description="This is your first task. Click to edit or delete it.",
            status="pending",
            priority="Normal",
            due_date = datetime.now(timezone.utc) + timedelta(days=7)
        )
        db.add(demo_task)
        db.commit()
        print(f"✅ Created demo task")

        print("\n🎉 Database initialized successfully!")
        print("\n📝 Login credentials:")
        print("   Email: demo@example.com")
        print("   Password: password123")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()