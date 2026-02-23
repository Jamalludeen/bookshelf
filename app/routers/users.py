from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from .. import crud, database, schemas


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    if crud.get_user_by_username(db=db, username=user.username):
        raise HTTPException(status_code=409, detail="Username already registered")

    if crud.get_user_by_email(db=db, email=user.email):
        raise HTTPException(status_code=409, detail="Email already registered")

    return crud.create_user(db=db, user=user)


@router.get("/", response_model=List[schemas.User])
def read_users(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(database.get_db),
):
    return crud.get_users(db=db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(database.get_db)):
    user = crud.get_user_by_id(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/{user_id}/tasks", response_model=List[schemas.Task])
def read_user_tasks(
    user_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(database.get_db),
):
    user = crud.get_user_by_id(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.get_user_tasks(db=db, user_id=user_id, skip=skip, limit=limit)
