# TaskMaster API

![status badge](https://img.shields.io/badge/status-active-brightgreen) Maintained

TaskMaster is a small FastAPI project for managing users and tasks.

Interactive docs are available at `/docs` and `/redoc` when the server is running.

OpenAPI schema is available at `/openapi.json`.

The `/docs` page is the quickest place to try requests during development.

The `/redoc` page is useful for a more readable API reference.

Use `/openapi.json` when you need schema-driven client generation.

## Quick start

1. Create and activate a virtual environment.
2. Install dependencies:

   pip install fastapi uvicorn sqlalchemy passlib[bcrypt]

3. Run the API:

   uvicorn app.main:app --reload

   or

   make run

Quick check:

curl -s http://127.0.0.1:8000/health

Health details:

curl -s http://127.0.0.1:8000/health/db

Readiness probe:

curl -s http://127.0.0.1:8000/health/ready

Version check:

curl -s http://127.0.0.1:8000/version

curl -s http://127.0.0.1:8000/

Maintainer: maintainer@example.com

Commit style: small, focused commits. See CONTRIBUTING for tips.
App version: 0.1.2

## Notes

- The SQLite database file is created at `sql_app.db` in this folder.
- This project uses SQLAlchemy models with a simple CRUD layer.
- See `.env.example` for environment variable defaults.
- Override `DATABASE_URL` in your environment to switch databases.

## Endpoints

Base URLs are listed with common query parameters.

### Users

- POST /users
- GET /users?skip=0&limit=100&username_query=&email_query=&is_active=&sort_by=&sort_dir=
- GET /users/active?skip=0&limit=100&sort_by=&sort_dir=
- GET /users/inactive?skip=0&limit=100&sort_by=&sort_dir=
- GET /users/by-username/{username}
- GET /users/{user_id}/exists
- GET /users/summary
- GET /users/export?username_query=&email_query=&is_active=&sort_by=&sort_dir=
- PATCH /users/{user_id}/status
- GET /users/{user_id}
- GET /users/{user_id}/summary
- GET /users/{user_id}/tasks?skip=0&limit=100
- GET /users/{user_id}/tasks/export
- DELETE /users/{user_id}

### Tasks

- POST /tasks
- GET /tasks?skip=0&limit=100&completed=&owner_id=&title_query=&description_query=&sort_by=&sort_dir=
- GET /tasks/summary?owner_id=
- GET /tasks/owner/{owner_id}/summary
- GET /tasks/completed?skip=0&limit=100&owner_id=&sort_by=&sort_dir=
- GET /tasks/pending?skip=0&limit=100&owner_id=&sort_by=&sort_dir=
- GET /tasks/{task_id}
- GET /tasks/{task_id}/status
- GET /tasks/{task_id}/exists
- GET /tasks/{task_id}/owner
- PUT /tasks/{task_id}
- PATCH /tasks/{task_id}
- PATCH /tasks/{task_id}/complete
- PATCH /tasks/{task_id}/reopen
- PATCH /tasks/{task_id}/toggle
- PATCH /tasks/bulk/complete
- PATCH /tasks/bulk/reopen
- DELETE /tasks/bulk
- GET /tasks/export?completed=&owner_id=&title_query=&description_query=&sort_by=&sort_dir=
- DELETE /tasks/{task_id}

### System

- GET /
- GET /health
- GET /health/live
- GET /health/ready
- GET /health/db
- GET /version
- GET /stats
- GET /uptime

Tip: `GET /uptime` is useful for quick process restarts verification.

Notes:

- `GET /` returns both a welcome message and API version.
- `GET /health` returns `503` when the database is unreachable.
- `GET /health/live` is a lightweight process liveness probe.
- `GET /health/ready` is a readiness probe that verifies database access.
- `GET /uptime` returns process start time and uptime in seconds.
- System endpoints are grouped under the `system` tag in OpenAPI docs.

### Data handling

- Usernames are trimmed before storage and uniqueness checks.
- Emails are trimmed and lowercased before storage and uniqueness checks.

## Response headers

- `GET /users`, `GET /users/{user_id}/tasks`, and `GET /tasks` include `X-Total-Count` for total records matching filters.
- All responses include `X-Request-ID`, `X-Process-Time`, `X-API-Version`, and `X-Service-Name` for tracing and diagnostics.
- System endpoints also include `Cache-Control: no-store` to prevent stale health/status caching.
- Send `X-Request-ID` in requests to propagate your own correlation id across logs.

## Export support

- `GET /users/export` downloads filtered user data as CSV.
- `GET /tasks/export` downloads filtered task data as CSV.
