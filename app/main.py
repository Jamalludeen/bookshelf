from time import perf_counter
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request, Response
import logging
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from . import crud, database, models, schemas
from .routers import all_routers

# Create Database Tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="TaskMaster API",
    description="A simple API for managing users and tasks.",
    version="0.1.2",
    contact={"name": "TaskMaster Maintainers"},
    license_info={"name": "MIT"},
    openapi_tags=[
        {"name": "tasks", "description": "Task management operations"},
        {"name": "users", "description": "User management operations"},
        {"name": "system", "description": "System and diagnostics endpoints"},
    ],
)

APP_STARTED_AT = datetime.now(timezone.utc)
SERVICE_NAME = "TaskMaster API"

# Basic logging configuration for quick runtime diagnostics
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("taskmaster")
logger.info("TaskMaster application module loaded")
# Log format stays intentionally simple for local debugging.

# include routers from routers package
for _r in all_routers:
    app.include_router(_r)


@app.on_event("startup")
def on_startup():
    # Log a masked DB URL and app version for quick diagnostics
    try:
        masked = database.masked_database_url()
    except Exception:
        masked = "unknown"
    # This helps confirm which configuration the app booted with.
    # Keep startup logs short so they stay readable in local terminals.
    # The version string makes it obvious which build is running.
    logger.info("startup: version=%s db=%s", app.version, masked)


@app.middleware("http")
async def add_observability_headers(request: Request, call_next):
    # Preserve inbound request id when available for cross-service tracing.
    # Fall back to a generated UUID when clients do not provide one.
    request_id = request.headers.get("x-request-id", str(uuid4()))
    start_time = perf_counter()
    response = await call_next(request)
    process_time = perf_counter() - start_time
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{process_time:.6f}"
    response.headers["X-API-Version"] = app.version
    response.headers["X-Service-Name"] = SERVICE_NAME
    return response


@app.middleware("http")
async def disable_cache_for_system_endpoints(request: Request, call_next):
    # Health and status endpoints should not be cached by intermediaries.
    response = await call_next(request)
    if request.url.path in {
        "/",
        "/health",
        "/health/live",
        "/health/ready",
        "/health/db",
        "/version",
        "/stats",
        "/uptime",
    }:
        response.headers["Cache-Control"] = "no-store"
    return response


@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
    logger.error("HTTPException: status=%s detail=%s path=%s", exc.status_code, exc.detail, request.url.path)
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


def _is_database_reachable() -> bool:
    try:
        with database.engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except (SQLAlchemyError, Exception):
        return False
    return True

@app.get("/", tags=["system"], response_model=schemas.RootInfo)
def root():
    return {
        "message": "Welcome to TaskMaster",
        "version": app.version,
    }


@app.get("/health", tags=["system"], response_model=schemas.HealthInfo)
def health_check(response: Response):
    checked_at = datetime.now(timezone.utc)
    if not _is_database_reachable():
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
    if not _is_database_reachable():
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


@app.get("/health/db", tags=["system"], response_model=schemas.DatabaseHealthInfo)
def database_health(response: Response):
    checked_at = datetime.now(timezone.utc)
    reachable = _is_database_reachable()
    if not reachable:
        response.status_code = 503
    return {
        "reachable": reachable,
        "checked_at": checked_at,
    }


@app.get("/version", tags=["system"], response_model=schemas.VersionInfo)
def version():
    return {"version": app.version}


@app.get("/stats", tags=["system"], response_model=schemas.SystemStats)
def system_stats():
    with database.SessionLocal() as db:
        return crud.get_system_stats(db=db)


@app.get("/uptime", tags=["system"], response_model=schemas.UptimeInfo)
def uptime_info():
    now = datetime.now(timezone.utc)
    return {
        "started_at": APP_STARTED_AT,
        "uptime_seconds": (now - APP_STARTED_AT).total_seconds(),
    }
