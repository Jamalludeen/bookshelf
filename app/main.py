from fastapi import FastAPI
from . import database, models
from .routers import tasks, users

# Create Database Tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="TaskMaster API",
    description="A simple API for managing users and tasks.",
    version="0.1.0",
)

# app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(users.router)

@app.get("/")
def root():
    return {"message": "Welcome to TaskMaster"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
