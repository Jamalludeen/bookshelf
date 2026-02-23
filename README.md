# TaskMaster API

TaskMaster is a small FastAPI project for managing users and tasks.

## Quick start

1. Create and activate a virtual environment.
2. Install dependencies:

   pip install fastapi uvicorn sqlalchemy passlib[bcrypt]

3. Run the API:

   uvicorn app.main:app --reload

## Notes

- The SQLite database file is created at `sql_app.db` in this folder.
- This project uses SQLAlchemy models with a simple CRUD layer.

## Endpoints

Base URLs are listed with common query parameters.

### Users

- POST /users
- GET /users?skip=0&limit=100&username_query=&email_query=
- GET /users/{user_id}
- GET /users/{user_id}/tasks?skip=0&limit=100

### Tasks

- POST /tasks
- GET /tasks?skip=0&limit=100&completed=&owner_id=&title_query=&sort_by=&sort_dir=
- GET /tasks/summary?owner_id=
- GET /tasks/{task_id}
- PATCH /tasks/{task_id}
- PATCH /tasks/{task_id}/complete
- DELETE /tasks/{task_id}

### System

- GET /
- GET /health
