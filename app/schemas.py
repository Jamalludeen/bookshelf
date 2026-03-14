from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional, Literal


TaskSortBy = Literal["id", "title", "completed"]
TaskSortDir = Literal["asc", "desc"]
UserSortBy = Literal["id", "username", "email", "is_active"]
UserSortDir = Literal["asc", "desc"]


class TaskBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = False

    @validator("title")
    def validate_title(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("title must not be blank")
        return stripped

class TaskCreate(TaskBase):
    owner_id: int = Field(gt=0)


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: Optional[bool] = None


class TaskBulkUpdateRequest(BaseModel):
    task_ids: List[int] = Field(min_items=1)

    @validator("task_ids")
    def validate_task_ids(cls, value: List[int]) -> List[int]:
        if any(task_id <= 0 for task_id in value):
            raise ValueError("task_ids must contain only positive integers")
        return value

class Task(TaskBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr

    @validator("username")
    def validate_username(cls, value: str) -> str:
        stripped = value.strip()
        if len(stripped) < 3:
            raise ValueError("username must be at least 3 characters")
        return stripped

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


class UserSummary(BaseModel):
    total: int
    active: int
    inactive: int
    with_tasks: int
    without_tasks: int


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
    checked_at: datetime


class LivenessInfo(BaseModel):
    status: Literal["alive"]
    version: str
    checked_at: datetime


class ReadinessInfo(BaseModel):
    status: Literal["ready", "not_ready"]
    database: Literal["reachable", "unreachable"]
    checked_at: datetime
        