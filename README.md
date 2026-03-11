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
- GET /users?skip=0&limit=100&username_query=&email_query=&is_active=
- PATCH /users/{user_id}/status
- GET /users/{user_id}
- GET /users/{user_id}/tasks?skip=0&limit=100

### Tasks

- POST /tasks
- GET /tasks?skip=0&limit=100&completed=&owner_id=&title_query=&description_query=&sort_by=&sort_dir=
- GET /tasks/summary?owner_id=
- GET /tasks/{task_id}
- PATCH /tasks/{task_id}
- PATCH /tasks/{task_id}/complete
- PATCH /tasks/{task_id}/reopen
- PATCH /tasks/bulk/complete
- PATCH /tasks/bulk/reopen
- DELETE /tasks/{task_id}

### System

- GET /
- GET /health
- GET /version

Notes:

- `GET /` returns both a welcome message and API version.
- `GET /health` returns `503` when the database is unreachable.
- System endpoints are grouped under the `system` tag in OpenAPI docs.

### Data handling

- Usernames are trimmed before storage and uniqueness checks.
- Emails are trimmed and lowercased before storage and uniqueness checks.

## Response headers

- `GET /users`, `GET /users/{user_id}/tasks`, and `GET /tasks` include `X-Total-Count` for total records matching filters.
- All responses include `X-Request-ID` and `X-Process-Time` for request tracing and timing.
