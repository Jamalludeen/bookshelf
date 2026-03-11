from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response, status
from sqlalchemy.orm import Session

from .. import crud, database, schemas


router = APIRouter(prefix="/users", tags=["users"])


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
    limit: int = Query(default=100, ge=1, le=100),
    username_query: str | None = Query(default=None, max_length=50),
    email_query: str | None = Query(default=None, max_length=255),
    is_active: bool | None = Query(default=None),
    db: Session = Depends(database.get_db),
):
    users = crud.get_users(
        db=db,
        skip=skip,
        limit=limit,
        username_query=username_query,
        email_query=email_query,
        is_active=is_active,
    )
    total = crud.count_users(
        db=db,
        username_query=username_query,
        email_query=email_query,
        is_active=is_active,
    )
    response.headers["X-Total-Count"] = str(total)
    return users


@router.get("/{user_id}", response_model=schemas.User)
def read_user(user_id: int = Path(..., ge=1), db: Session = Depends(database.get_db)):
    user = crud.get_user_by_id(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/{user_id}/tasks", response_model=List[schemas.Task])
def read_user_tasks(
    response: Response,
    user_id: int = Path(..., ge=1),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(database.get_db),
):
    user = crud.get_user_by_id(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    tasks = crud.get_user_tasks(db=db, user_id=user_id, skip=skip, limit=limit)
    response.headers["X-Total-Count"] = str(crud.count_user_tasks(db=db, user_id=user_id))
    return tasks


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
