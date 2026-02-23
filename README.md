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
