from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from . import database, models
from .routers import tasks, users

# Create Database Tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="TaskMaster API",
    description="A simple API for managing users and tasks.",
    version="0.1.0",
    openapi_tags=[
        {"name": "tasks", "description": "Task management operations"},
        {"name": "users", "description": "User management operations"},
    ],
)

# app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(users.router)

@app.get("/")
def root():
    return {"message": "Welcome to TaskMaster"}


@app.get("/health")
def health_check():
    try:
        with database.engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return {
            "status": "degraded",
            "database": "unreachable",
            "version": app.version,
        }

    return {
        "status": "ok",
        "database": "reachable",
        "version": app.version,
    }


@app.get("/version")
def version():
    return {"version": app.version}
