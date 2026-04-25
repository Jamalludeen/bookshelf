import csv
from io import StringIO

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from .. import crud, database, schemas
import logging


logger = logging.getLogger("taskmaster.users")
logger.debug("users router loaded")


# User-related endpoints live under `/users`.
router = APIRouter(prefix="/users", tags=["users"])

DEFAULT_LIMIT = 100
MAX_LIMIT = 100


def _normalize_optional_query(value: str | None) -> str | None:
    # Treat whitespace-only query values as absent.
    if value is None:
        return None
    normalized = value.strip()
    # Return None so downstream filters can skip this parameter.
    return normalized or None


@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    normalized_username = user.username.strip()
    normalized_email = user.email.strip().lower()

    if crud.get_user_by_username(db=db, username=normalized_username):
        raise HTTPException(status_code=409, detail="Username already registered")

    if crud.get_user_by_email(db=db, email=normalized_email):
        raise HTTPException(status_code=409, detail="Email already registered")

    return crud.create_user(db=db, user=user)


@router.get("/", response_model=List[schemas.User])
def read_users(
    response: Response,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
    username_query: str | None = Query(default=None, max_length=50),
    email_query: str | None = Query(default=None, max_length=255),
    is_active: bool | None = Query(default=None),
    sort_by: schemas.UserSortBy = Query(default="id"),
    sort_dir: schemas.UserSortDir = Query(default="asc"),
    db: Session = Depends(database.get_db),
):
    normalized_username_query = _normalize_optional_query(username_query)
    normalized_email_query = _normalize_optional_query(email_query)
    # Keep filter handling centralized in CRUD helpers.
    # This keeps the router thin and easier to scan.
    users = crud.get_users(
        db=db,
        skip=skip,
        limit=limit,
        username_query=normalized_username_query,
        email_query=normalized_email_query,
        is_active=is_active,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    total = crud.count_users(
        db=db,
        username_query=normalized_username_query,
        email_query=normalized_email_query,
        is_active=is_active,
    )
    response.headers["X-Total-Count"] = str(total)
    return users


@router.get("/active", response_model=List[schemas.User])
def read_active_users(
    response: Response,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
    sort_by: schemas.UserSortBy = Query(default="id"),
    sort_dir: schemas.UserSortDir = Query(default="asc"),
    db: Session = Depends(database.get_db),
):
    users = crud.get_users(
        db=db,
        skip=skip,
        limit=limit,
        is_active=True,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    total = crud.count_users(db=db, is_active=True)
    response.headers["X-Total-Count"] = str(total)
    return users


@router.get("/inactive", response_model=List[schemas.User])
def read_inactive_users(
    response: Response,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
    sort_by: schemas.UserSortBy = Query(default="id"),
    sort_dir: schemas.UserSortDir = Query(default="asc"),
    db: Session = Depends(database.get_db),
):
    users = crud.get_users(
        db=db,
        skip=skip,
        limit=limit,
        is_active=False,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    total = crud.count_users(db=db, is_active=False)
    response.headers["X-Total-Count"] = str(total)
    return users


@router.get("/by-username/{username}", response_model=schemas.UserPublic)
def read_user_by_username(username: str, db: Session = Depends(database.get_db)):
    normalized_username = username.strip()
    if not normalized_username:
        raise HTTPException(status_code=400, detail="Username must not be blank")

    user = crud.get_user_by_username(db=db, username=normalized_username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/{user_id}/exists", response_model=schemas.ExistsInfo)
def read_user_exists(user_id: int = Path(..., ge=1), db: Session = Depends(database.get_db)):
    return {"exists": crud.user_exists(db=db, user_id=user_id)}


@router.get("/summary", response_model=schemas.UserSummary)
def read_user_summary(db: Session = Depends(database.get_db)):
    # Summary endpoint gives a lightweight aggregate for dashboards.
    return crud.get_user_summary(db=db)


@router.get("/export")
def export_users_csv(
    username_query: str | None = Query(default=None, max_length=50),
    email_query: str | None = Query(default=None, max_length=255),
    is_active: bool | None = Query(default=None),
    sort_by: schemas.UserSortBy = Query(default="id"),
    sort_dir: schemas.UserSortDir = Query(default="asc"),
    db: Session = Depends(database.get_db),
):
    # Export respects the same filter/query semantics as list users.
    normalized_username_query = _normalize_optional_query(username_query)
    normalized_email_query = _normalize_optional_query(email_query)
    total = crud.count_users(
        db=db,
        username_query=normalized_username_query,
        email_query=normalized_email_query,
        is_active=is_active,
    )
    users = crud.get_users(
        db=db,
        skip=0,
        limit=max(total, 1),
        username_query=normalized_username_query,
        email_query=normalized_email_query,
        is_active=is_active,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )

    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["id", "username", "email", "is_active", "task_count"])
    for user in users:
        writer.writerow([
            user.id,
            user.username,
            user.email,
            str(user.is_active).lower(),
            len(user.tasks),
        ])
    buffer.seek(0)

    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="users.csv"'},
    )


@router.get("/{user_id}", response_model=schemas.User)
def read_user(user_id: int = Path(..., ge=1), db: Session = Depends(database.get_db)):
    user = crud.get_user_by_id(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/{user_id}/summary", response_model=schemas.UserTaskSummary)
def read_user_task_summary(user_id: int = Path(..., ge=1), db: Session = Depends(database.get_db)):
    if not crud.user_exists(db=db, user_id=user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return crud.get_user_task_summary(db=db, user_id=user_id)


@router.get("/{user_id}/tasks", response_model=List[schemas.Task])
def read_user_tasks(
    response: Response,
    user_id: int = Path(..., ge=1),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
    db: Session = Depends(database.get_db),
):
    if not crud.user_exists(db=db, user_id=user_id):
        raise HTTPException(status_code=404, detail="User not found")
    tasks = crud.get_user_tasks(db=db, user_id=user_id, skip=skip, limit=limit)
    response.headers["X-Total-Count"] = str(crud.count_user_tasks(db=db, user_id=user_id))
    return tasks


@router.get("/{user_id}/tasks/export")
def export_user_tasks_csv(user_id: int = Path(..., ge=1), db: Session = Depends(database.get_db)):
    if not crud.user_exists(db=db, user_id=user_id):
        raise HTTPException(status_code=404, detail="User not found")

    total = crud.count_user_tasks(db=db, user_id=user_id)
    tasks = crud.get_user_tasks(db=db, user_id=user_id, skip=0, limit=max(total, 1))

    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["id", "title", "description", "completed", "owner_id"])
    for task in tasks:
        writer.writerow([
            task.id,
            task.title,
            task.description or "",
            str(task.completed).lower(),
            task.owner_id,
        ])
    buffer.seek(0)

    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="user-{user_id}-tasks.csv"'},
    )


@router.patch("/{user_id}/status", response_model=schemas.User)
def update_user_status(
    payload: schemas.UserStatusUpdate,
    user_id: int = Path(..., ge=1),
    db: Session = Depends(database.get_db),
):
    user = crud.update_user_status(db=db, user_id=user_id, is_active=payload.is_active)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}", response_model=schemas.Message, status_code=status.HTTP_200_OK)
def delete_user(user_id: int = Path(..., ge=1), db: Session = Depends(database.get_db)):
    user = crud.delete_user(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": "User deleted successfully"}
