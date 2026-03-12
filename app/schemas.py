from pydantic import BaseModel, EmailStr, Field, conint, constr
from typing import List, Optional, Literal


TaskSortBy = Literal["id", "title", "completed"]
TaskSortDir = Literal["asc", "desc"]


class TaskBase(BaseModel):
    title: constr(strip_whitespace=True, min_length=1, max_length=200)
    description: Optional[constr(max_length=1000)] = None
    completed: bool = False

class TaskCreate(TaskBase):
    owner_id: conint(gt=0)


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: Optional[bool] = None


class TaskBulkUpdateRequest(BaseModel):
    task_ids: List[conint(gt=0)] = Field(min_items=1)

class Task(TaskBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: constr(strip_whitespace=True, min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserStatusUpdate(BaseModel):
    is_active: bool

class User(UserBase):
    id: int
    is_active: bool
    tasks: List[Task] = []

    class Config:
        orm_mode = True


class TaskSummary(BaseModel):
    total: int
    completed: int
    pending: int


class Message(BaseModel):
    detail: str


class RootInfo(BaseModel):
    message: str
    version: str


class VersionInfo(BaseModel):
    version: str


class HealthInfo(BaseModel):
    status: Literal["ok", "degraded"]
    database: Literal["reachable", "unreachable"]
    version: str
        