import csv
from io import StringIO

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import crud, database, schemas

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)


def _normalize_optional_query(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _ensure_unique_task_ids(task_ids: list[int]) -> None:
    if len(task_ids) != len(set(task_ids)):
        raise HTTPException(status_code=400, detail="task_ids must contain unique values")

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
    response: Response,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    completed: Optional[bool] = None,
    owner_id: Optional[int] = Query(default=None, ge=1),
    title_query: Optional[str] = Query(default=None, max_length=200),
    description_query: Optional[str] = Query(default=None, max_length=1000),
    sort_by: schemas.TaskSortBy = Query(default="id"),
    sort_dir: schemas.TaskSortDir = Query(default="asc"),
    db: Session = Depends(database.get_db)
):
    normalized_title_query = _normalize_optional_query(title_query)
    normalized_description_query = _normalize_optional_query(description_query)
    tasks = crud.get_tasks(
        db,
        skip=skip,
        limit=limit,
        completed=completed,
        owner_id=owner_id,
        title_query=normalized_title_query,
        description_query=normalized_description_query,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    total = crud.count_tasks(
        db=db,
        completed=completed,
        owner_id=owner_id,
        title_query=normalized_title_query,
        description_query=normalized_description_query,
    )
    response.headers["X-Total-Count"] = str(total)
    return tasks


@router.get("/summary", response_model=schemas.TaskSummary)
def read_task_summary(
    owner_id: Optional[int] = Query(default=None, ge=1),
    db: Session = Depends(database.get_db),
):
    return crud.get_task_summary(db=db, owner_id=owner_id)


@router.get("/completed", response_model=List[schemas.Task])
def read_completed_tasks(
    response: Response,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    owner_id: Optional[int] = Query(default=None, ge=1),
    sort_by: schemas.TaskSortBy = Query(default="id"),
    sort_dir: schemas.TaskSortDir = Query(default="asc"),
    db: Session = Depends(database.get_db),
):
    tasks = crud.get_tasks(
        db=db,
        skip=skip,
        limit=limit,
        completed=True,
        owner_id=owner_id,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    total = crud.count_tasks(db=db, completed=True, owner_id=owner_id)
    response.headers["X-Total-Count"] = str(total)
    return tasks


@router.get("/pending", response_model=List[schemas.Task])
def read_pending_tasks(
    response: Response,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    owner_id: Optional[int] = Query(default=None, ge=1),
    sort_by: schemas.TaskSortBy = Query(default="id"),
    sort_dir: schemas.TaskSortDir = Query(default="asc"),
    db: Session = Depends(database.get_db),
):
    tasks = crud.get_tasks(
        db=db,
        skip=skip,
        limit=limit,
        completed=False,
        owner_id=owner_id,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    total = crud.count_tasks(db=db, completed=False, owner_id=owner_id)
    response.headers["X-Total-Count"] = str(total)
    return tasks


@router.patch("/bulk/complete", response_model=List[schemas.Task])
def complete_tasks_bulk(
    payload: schemas.TaskBulkUpdateRequest,
    db: Session = Depends(database.get_db),
):
    _ensure_unique_task_ids(payload.task_ids)
    tasks = crud.set_tasks_completed(db=db, task_ids=payload.task_ids)
    if not tasks:
        raise HTTPException(status_code=404, detail="No tasks found for provided IDs")
    return tasks


@router.patch("/bulk/reopen", response_model=List[schemas.Task])
def reopen_tasks_bulk(
    payload: schemas.TaskBulkUpdateRequest,
    db: Session = Depends(database.get_db),
):
    _ensure_unique_task_ids(payload.task_ids)
    tasks = crud.set_tasks_incomplete(db=db, task_ids=payload.task_ids)
    if not tasks:
        raise HTTPException(status_code=404, detail="No tasks found for provided IDs")
    return tasks


@router.delete("/bulk", response_model=schemas.Message, status_code=status.HTTP_200_OK)
def delete_tasks_bulk(
    payload: schemas.TaskBulkUpdateRequest,
    db: Session = Depends(database.get_db),
):
    _ensure_unique_task_ids(payload.task_ids)
    deleted_count = crud.delete_tasks(db=db, task_ids=payload.task_ids)
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="No tasks found for provided IDs")
    return {"detail": f"Deleted {deleted_count} task(s) successfully"}


@router.get("/export")
def export_tasks_csv(
    completed: Optional[bool] = None,
    owner_id: Optional[int] = Query(default=None, ge=1),
    title_query: Optional[str] = Query(default=None, max_length=200),
    description_query: Optional[str] = Query(default=None, max_length=1000),
    sort_by: schemas.TaskSortBy = Query(default="id"),
    sort_dir: schemas.TaskSortDir = Query(default="asc"),
    db: Session = Depends(database.get_db),
):
    normalized_title_query = _normalize_optional_query(title_query)
    normalized_description_query = _normalize_optional_query(description_query)
    total = crud.count_tasks(
        db=db,
        completed=completed,
        owner_id=owner_id,
        title_query=normalized_title_query,
        description_query=normalized_description_query,
    )
    tasks = crud.get_tasks(
        db=db,
        skip=0,
        limit=max(total, 1),
        completed=completed,
        owner_id=owner_id,
        title_query=normalized_title_query,
        description_query=normalized_description_query,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )

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
        headers={"Content-Disposition": 'attachment; filename="tasks.csv"'},
    )


@router.get("/{task_id}", response_model=schemas.Task)
def read_task(task_id: int = Path(..., ge=1), db: Session = Depends(database.get_db)):
    task = crud.get_task_by_id(db=db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get("/{task_id}/owner", response_model=schemas.UserPublic)
def read_task_owner(task_id: int = Path(..., ge=1), db: Session = Depends(database.get_db)):
    task = crud.get_task_by_id(db=db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    user = crud.get_user_by_id(db=db, user_id=task.owner_id)
    if not user:
        raise HTTPException(status_code=404, detail="Owner not found")
    return user


@router.patch("/{task_id}", response_model=schemas.Task)
def update_task(
    task_update: schemas.TaskUpdate,
    task_id: int = Path(..., ge=1),
    db: Session = Depends(database.get_db),
):
    if not task_update.dict(exclude_unset=True):
        raise HTTPException(status_code=400, detail="No fields provided for update")

    task = crud.update_task(db=db, task_id=task_id, task_update=task_update)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=schemas.Task)
def replace_task(
    task_replace: schemas.TaskReplace,
    task_id: int = Path(..., ge=1),
    db: Session = Depends(database.get_db),
):
    if not crud.get_user_by_id(db=db, user_id=task_replace.owner_id):
        raise HTTPException(status_code=404, detail="Owner not found")

    task = crud.replace_task(db=db, task_id=task_id, task_replace=task_replace)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}/complete", response_model=schemas.Task)
def complete_task(task_id: int = Path(..., ge=1), db: Session = Depends(database.get_db)):
    task = crud.set_task_completed(db=db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}/reopen", response_model=schemas.Task)
def reopen_task(task_id: int = Path(..., ge=1), db: Session = Depends(database.get_db)):
    task = crud.set_task_incomplete(db=db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}/toggle", response_model=schemas.Task)
def toggle_task(task_id: int = Path(..., ge=1), db: Session = Depends(database.get_db)):
    task = crud.toggle_task_completed(db=db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}", response_model=schemas.Message, status_code=status.HTTP_200_OK)
def delete_task(task_id: int = Path(..., ge=1), db: Session = Depends(database.get_db)):
    task = crud.delete_task(db=db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"detail": "Task deleted successfully"}