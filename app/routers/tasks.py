from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, database, schemas

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)

@router.post("/", response_model=schemas.Task)
def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(database.get_db),
):
    return crud.create_user_task(db=db, task=task)

@router.get("/", response_model=List[schemas.Task])
def read_tasks(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(database.get_db)
):
    tasks = crud.get_tasks(db, skip=skip, limit=limit)
    return tasks