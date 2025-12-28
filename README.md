# Task Management API

A RESTful API for managing users and tasks with full CRUD operations, built with FastAPI and SQLAlchemy.

## Features
- Multi-user task management with relational data modeling
- Full CRUD operations for users and tasks
- Input validation and proper HTTP status codes
- Task filtering by user
- Automatic CASCADE delete for data integrity
- Interactive API documentation (FastAPI auto-generated)

## Tech Stack
- **Framework:** FastAPI
- **Database:** SQLite (PostgreSQL-compatible)
- **ORM:** SQLAlchemy
- **Validation:** Pydantic
- **Python:** 3.10+

## Setup

1. Clone the repository
```bash
git clone <your-repo-url>
cd task-api
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Run the application
```bash
uvicorn app.main:app --reload
```

5. Access API documentation
- Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## Example Usage

### Create a user
```bash
curl -X POST "http://localhost:8000/users" \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice","email":"alice@example.com"}'
```

### Create a task
```bash
curl -X POST "http://localhost:8000/tasks" \
  -H "Content-Type: application/json" \
  -d '{"user_id":1,"title":"Complete project","status":"pending"}'
```

### Update task status
```bash
curl -X PATCH "http://localhost:8000/tasks/1" \
  -H "Content-Type: application/json" \
  -d '{"status":"completed"}'
```

### Get user's tasks
```bash
curl "http://localhost:8000/tasks?user_id=1"
```

## Data Models

### User
- `id`: Integer (auto-generated)
- `name`: String (required)
- `email`: String (required, unique)
- `created_at`: Datetime

### Task
- `id`: Integer (auto-generated)
- `user_id`: Integer (foreign key, required)
- `title`: String (required, max 200 chars)
- `description`: String (optional)
- `status`: Enum ("pending" | "in_progress" | "completed")
- `created_at`: Datetime
- `updated_at`: Datetime

## Design Decisions

- **No Authentication:** Focus on API design and data modeling. Authentication would be added as Phase 2 using JWT tokens.
- **CASCADE Delete:** Deleting a user automatically deletes their tasks to maintain referential integrity.
- **Free Status Transitions:** Tasks can move between any status states for flexibility.
- **SQLite for Development:** Easy local setup. Database design is PostgreSQL-compatible for production migration.


## Future Enhancements

- JWT-based authentication and authorization
- Task assignment and sharing between users
- Due dates and priority levels
- Pagination for large datasets
- Task search and advanced filtering
- API rate limiting
- Docker containerization

