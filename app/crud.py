from sqlalchemy.orm import Session
from typing import Optional
from . import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _unique_task_ids(task_ids: list[int]) -> list[int]:
    seen: set[int] = set()
    unique_ids: list[int] = []
    for task_id in task_ids:
        if task_id in seen:
            continue
        seen.add(task_id)
        unique_ids.append(task_id)
    return unique_ids


def _normalize_text(value: str) -> str:
    return value.strip()


def _normalize_email(value: str) -> str:
    return value.strip().lower()


def _normalize_optional_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    return value.strip()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_users(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    username_query: Optional[str] = None,
    email_query: Optional[str] = None,
    is_active: Optional[bool] = None,
    sort_by: schemas.UserSortBy = "id",
    sort_dir: schemas.UserSortDir = "asc",
):
    query = db.query(models.User)
    if username_query:
        query = query.filter(models.User.username.ilike(f"%{username_query}%"))
    if email_query:
        query = query.filter(models.User.email.ilike(f"%{email_query}%"))
    if is_active is not None:
        query = query.filter(models.User.is_active == is_active)

    sort_map = {
        "id": models.User.id,
        "username": models.User.username,
        "email": models.User.email,
        "is_active": models.User.is_active,
    }
    sort_column = sort_map.get(sort_by, models.User.id)
    if sort_dir == "desc":
        query = query.order_by(sort_column.desc(), models.User.id.desc())
    else:
        query = query.order_by(sort_column.asc(), models.User.id.asc())

    return query.offset(skip).limit(limit).all()


def count_users(
    db: Session,
    username_query: Optional[str] = None,
    email_query: Optional[str] = None,
    is_active: Optional[bool] = None,
):
    query = db.query(models.User)
    if username_query:
        query = query.filter(models.User.username.ilike(f"%{username_query}%"))
    if email_query:
        query = query.filter(models.User.email.ilike(f"%{email_query}%"))
    if is_active is not None:
        query = query.filter(models.User.is_active == is_active)
    return query.count()


def get_user_tasks(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Task)
        .filter(models.Task.owner_id == user_id)
        .order_by(models.Task.id.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def count_user_tasks(db: Session, user_id: int):
    return db.query(models.Task).filter(models.Task.owner_id == user_id).count()


def get_user_summary(db: Session):
    total = db.query(models.User).count()
    active = db.query(models.User).filter(models.User.is_active.is_(True)).count()
    inactive = total - active
    with_tasks = (
        db.query(models.User.id)
        .join(models.Task, models.Task.owner_id == models.User.id)
        .distinct()
        .count()
    )
    without_tasks = total - with_tasks
    return {
        "total": total,
        "active": active,
        "inactive": inactive,
        "with_tasks": with_tasks,
        "without_tasks": without_tasks,
    }


def get_user_task_summary(db: Session, user_id: int):
    base_query = db.query(models.Task).filter(models.Task.owner_id == user_id)
    total = base_query.count()
    completed = base_query.filter(models.Task.completed.is_(True)).count()
    pending = total - completed
    return {
        "user_id": user_id,
        "total": total,
        "completed": completed,
        "pending": pending,
    }

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        email=_normalize_email(user.email),
        username=_normalize_text(user.username),
        hashed_password=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_status(db: Session, user_id: int, is_active: bool):
    db_user = get_user_by_id(db=db, user_id=user_id)
    if not db_user:
        return None

    db_user.is_active = is_active
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    db_user = get_user_by_id(db=db, user_id=user_id)
    if not db_user:
        return None

    db.delete(db_user)
    db.commit()
    return db_user

def get_tasks(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    completed: Optional[bool] = None,
    owner_id: Optional[int] = None,
    title_query: Optional[str] = None,
    description_query: Optional[str] = None,
    sort_by: schemas.TaskSortBy = "id",
    sort_dir: schemas.TaskSortDir = "asc",
):
    query = db.query(models.Task)
    if completed is not None:
        query = query.filter(models.Task.completed == completed)
    if owner_id is not None:
        query = query.filter(models.Task.owner_id == owner_id)
    if title_query:
        query = query.filter(models.Task.title.ilike(f"%{title_query}%"))
    if description_query:
        query = query.filter(models.Task.description.ilike(f"%{description_query}%"))

    sort_map = {
        "id": models.Task.id,
        "title": models.Task.title,
        "completed": models.Task.completed,
    }
    sort_column = sort_map.get(sort_by, models.Task.id)
    if sort_dir == "desc":
        query = query.order_by(sort_column.desc(), models.Task.id.desc())
    else:
        query = query.order_by(sort_column.asc(), models.Task.id.asc())

    return query.offset(skip).limit(limit).all()


def count_tasks(
    db: Session,
    completed: Optional[bool] = None,
    owner_id: Optional[int] = None,
    title_query: Optional[str] = None,
    description_query: Optional[str] = None,
):
    query = db.query(models.Task)
    if completed is not None:
        query = query.filter(models.Task.completed == completed)
    if owner_id is not None:
        query = query.filter(models.Task.owner_id == owner_id)
    if title_query:
        query = query.filter(models.Task.title.ilike(f"%{title_query}%"))
    if description_query:
        query = query.filter(models.Task.description.ilike(f"%{description_query}%"))
    return query.count()


def get_task_by_id(db: Session, task_id: int):
    return db.query(models.Task).filter(models.Task.id == task_id).first()

def create_user_task(db: Session, task: schemas.TaskCreate, user_id: int):
    task_data = task.dict()
    task_data["title"] = _normalize_text(task_data["title"])
    task_data["description"] = _normalize_optional_text(task_data.get("description"))
    db_task = models.Task(**task_data, owner_id=user_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def update_task(db: Session, task_id: int, task_update: schemas.TaskUpdate):
    db_task = get_task_by_id(db=db, task_id=task_id)
    if not db_task:
        return None

    update_data = task_update.dict(exclude_unset=True)
    if "title" in update_data and update_data["title"] is not None:
        update_data["title"] = _normalize_text(update_data["title"])
    if "description" in update_data:
        update_data["description"] = _normalize_optional_text(update_data["description"])

    for field, value in update_data.items():
        setattr(db_task, field, value)

    db.commit()
    db.refresh(db_task)
    return db_task


def get_task_summary(db: Session, owner_id: Optional[int] = None):
    base_query = db.query(models.Task)
    if owner_id is not None:
        base_query = base_query.filter(models.Task.owner_id == owner_id)

    total = base_query.count()
    completed_query = db.query(models.Task).filter(models.Task.completed.is_(True))
    if owner_id is not None:
        completed_query = completed_query.filter(models.Task.owner_id == owner_id)

    completed = completed_query.count()
    pending = total - completed
    return {"total": total, "completed": completed, "pending": pending}


def set_task_completed(db: Session, task_id: int):
    db_task = get_task_by_id(db=db, task_id=task_id)
    if not db_task:
        return None

    db_task.completed = True
    db.commit()
    db.refresh(db_task)
    return db_task


def set_task_incomplete(db: Session, task_id: int):
    db_task = get_task_by_id(db=db, task_id=task_id)
    if not db_task:
        return None

    db_task.completed = False
    db.commit()
    db.refresh(db_task)
    return db_task


def toggle_task_completed(db: Session, task_id: int):
    db_task = get_task_by_id(db=db, task_id=task_id)
    if not db_task:
        return None

    db_task.completed = not db_task.completed
    db.commit()
    db.refresh(db_task)
    return db_task


def set_tasks_completed(db: Session, task_ids: list[int]):
    unique_ids = _unique_task_ids(task_ids)
    tasks = db.query(models.Task).filter(models.Task.id.in_(unique_ids)).all()
    if not tasks:
        return []

    for task in tasks:
        task.completed = True
    db.commit()

    for task in tasks:
        db.refresh(task)
    return tasks


def set_tasks_incomplete(db: Session, task_ids: list[int]):
    unique_ids = _unique_task_ids(task_ids)
    tasks = db.query(models.Task).filter(models.Task.id.in_(unique_ids)).all()
    if not tasks:
        return []

    for task in tasks:
        task.completed = False
    db.commit()

    for task in tasks:
        db.refresh(task)
    return tasks


def delete_tasks(db: Session, task_ids: list[int]):
    unique_ids = _unique_task_ids(task_ids)
    tasks = db.query(models.Task).filter(models.Task.id.in_(unique_ids)).all()
    if not tasks:
        return 0

    deleted_count = len(tasks)
    for task in tasks:
        db.delete(task)
    db.commit()
    return deleted_count


def delete_task(db: Session, task_id: int):
    db_task = get_task_by_id(db=db, task_id=task_id)
    if not db_task:
        return None

    db.delete(db_task)
    db.commit()
    return db_task

