from sqlalchemy.orm import Session
from typing import Optional
from . import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(email=user.email, username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_tasks(db: Session, skip: int = 0, limit: int = 100, completed: Optional[bool] = None):
    query = db.query(models.Task)
    if completed is not None:
        query = query.filter(models.Task.completed == completed)
    return query.offset(skip).limit(limit).all()


def get_task_by_id(db: Session, task_id: int):
    return db.query(models.Task).filter(models.Task.id == task_id).first()

def create_user_task(db: Session, task: schemas.TaskCreate, user_id: int):
    db_task = models.Task(**task.dict(), owner_id=user_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


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

