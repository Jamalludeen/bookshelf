from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
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
    owner_id: Optional[int] = Query(default=None, ge=1),
    title_query: Optional[str] = Query(default=None, max_length=200),
    sort_by: str = Query(default="id", regex="^(id|title|completed)$"),
    sort_dir: str = Query(default="asc", regex="^(asc|desc)$"),
    db: Session = Depends(database.get_db)
):
    tasks = crud.get_tasks(
        db,
        skip=skip,
        limit=limit,
        completed=completed,
        owner_id=owner_id,
        title_query=title_query,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    return tasks


@router.get("/summary", response_model=schemas.TaskSummary)
def read_task_summary(
    owner_id: Optional[int] = Query(default=None, ge=1),
    db: Session = Depends(database.get_db),
):
    return crud.get_task_summary(db=db, owner_id=owner_id)


@router.get("/{task_id}", response_model=schemas.Task)
def read_task(task_id: int = Path(..., ge=1), db: Session = Depends(database.get_db)):
    task = crud.get_task_by_id(db=db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}", response_model=schemas.Task)
def update_task(
    task_id: int = Path(..., ge=1),
    task_update: schemas.TaskUpdate,
    db: Session = Depends(database.get_db),
):
    task = crud.update_task(db=db, task_id=task_id, task_update=task_update)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}/complete", response_model=schemas.Task)
def complete_task(task_id: int = Path(..., ge=1), db: Session = Depends(database.get_db)):
    task = crud.set_task_completed(db=db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}", response_model=schemas.Message, status_code=status.HTTP_200_OK)
def delete_task(task_id: int = Path(..., ge=1), db: Session = Depends(database.get_db)):
    task = crud.delete_task(db=db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"detail": "Task deleted successfully"}