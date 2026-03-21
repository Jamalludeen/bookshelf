from time import perf_counter
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from . import database, models, schemas
from .routers import tasks, users

# Create Database Tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="TaskMaster API",
    description="A simple API for managing users and tasks.",
    version="0.1.0",
    contact={"name": "TaskMaster Maintainers"},
    license_info={"name": "MIT"},
    openapi_tags=[
        {"name": "tasks", "description": "Task management operations"},
        {"name": "users", "description": "User management operations"},
        {"name": "system", "description": "System and diagnostics endpoints"},
    ],
)

# app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(users.router)


@app.middleware("http")
async def add_observability_headers(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid4()))
    start_time = perf_counter()
    response = await call_next(request)
    process_time = perf_counter() - start_time
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{process_time:.6f}"
    response.headers["X-API-Version"] = app.version
    return response


@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "path": request.url.path,
        },
    )


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": exc.errors(),
            "path": request.url.path,
        },
    )

@app.get("/", tags=["system"], response_model=schemas.RootInfo)
def root():
    return {
        "message": "Welcome to TaskMaster",
        "version": app.version,
    }


@app.get("/health", tags=["system"], response_model=schemas.HealthInfo)
def health_check(response: Response):
    checked_at = datetime.now(timezone.utc)
    try:
        with database.engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except (SQLAlchemyError, Exception):
        response.status_code = 503
        return {
            "status": "degraded",
            "database": "unreachable",
            "version": app.version,
            "checked_at": checked_at,
        }

    return {
        "status": "ok",
        "database": "reachable",
        "version": app.version,
        "checked_at": checked_at,
    }


@app.get("/health/live", tags=["system"], response_model=schemas.LivenessInfo)
def liveness_check():
    return {
        "status": "alive",
        "version": app.version,
        "checked_at": datetime.now(timezone.utc),
    }


@app.get("/health/ready", tags=["system"], response_model=schemas.ReadinessInfo)
def readiness_check(response: Response):
    checked_at = datetime.now(timezone.utc)
    try:
        with database.engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except (SQLAlchemyError, Exception):
        response.status_code = 503
        return {
            "status": "not_ready",
            "database": "unreachable",
            "checked_at": checked_at,
        }

    return {
        "status": "ready",
        "database": "reachable",
        "checked_at": checked_at,
    }


@app.get("/version", tags=["system"], response_model=schemas.VersionInfo)
def version():
    return {"version": app.version}
