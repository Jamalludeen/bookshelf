from sqlalchemy.orm import Session
from typing import Optional
from . import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
):
    query = db.query(models.User)
    if username_query:
        query = query.filter(models.User.username.ilike(f"%{username_query}%"))
    if email_query:
        query = query.filter(models.User.email.ilike(f"%{email_query}%"))
    if is_active is not None:
        query = query.filter(models.User.is_active == is_active)
    return query.offset(skip).limit(limit).all()


def get_user_tasks(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Task)
        .filter(models.Task.owner_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(email=user.email, username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_tasks(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    completed: Optional[bool] = None,
    owner_id: Optional[int] = None,
    title_query: Optional[str] = None,
    description_query: Optional[str] = None,
    sort_by: str = "id",
    sort_dir: str = "asc",
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
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    return query.offset(skip).limit(limit).all()


def get_task_by_id(db: Session, task_id: int):
    return db.query(models.Task).filter(models.Task.id == task_id).first()

def create_user_task(db: Session, task: schemas.TaskCreate, user_id: int):
    db_task = models.Task(**task.dict(), owner_id=user_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def update_task(db: Session, task_id: int, task_update: schemas.TaskUpdate):
    db_task = get_task_by_id(db=db, task_id=task_id)
    if not db_task:
        return None

    update_data = task_update.dict(exclude_unset=True)
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


def delete_task(db: Session, task_id: int):
    db_task = get_task_by_id(db=db, task_id=task_id)
    if not db_task:
        return None

    db.delete(db_task)
    db.commit()
    return db_task

