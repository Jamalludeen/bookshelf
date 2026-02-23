from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import crud, database, schemas

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)

@router.post("/", response_model=schemas.Task, status_code=status.HTTP_201_CREATED)
def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(database.get_db),
):
    if not crud.get_user_by_id(db=db, user_id=task.owner_id):
        raise HTTPException(status_code=404, detail="Owner not found")
    return crud.create_user_task(db=db, task=task, user_id=task.owner_id)

@router.get("/", response_model=List[schemas.Task])
def read_tasks(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    completed: Optional[bool] = None,
    db: Session = Depends(database.get_db)
):
    tasks = crud.get_tasks(db, skip=skip, limit=limit, completed=completed)
    return tasks


@router.get("/{task_id}", response_model=schemas.Task)
def read_task(task_id: int, db: Session = Depends(database.get_db)):
    task = crud.get_task_by_id(db=db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}/complete", response_model=schemas.Task)
def complete_task(task_id: int, db: Session = Depends(database.get_db)):
    task = crud.set_task_completed(db=db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(database.get_db)):
    task = crud.delete_task(db=db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"detail": "Task deleted successfully"}