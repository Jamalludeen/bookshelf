"""API routers package."""

from .tasks import router as tasks_router
from .users import router as users_router
from typing import List
from fastapi import APIRouter

__all__ = ["tasks_router", "users_router"]

all_routers: List[APIRouter] = [tasks_router, users_router]
