from fastapi import FastAPI
from . import database, models
from .routers import tasks

# Create Database Tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="TaskMaster API")

# app.include_router(auth.router)
app.include_router(tasks.router)

@app.get("/")
def root():
    return {"message": "Welcome to TaskMaster"}
