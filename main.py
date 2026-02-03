from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, Header, HTTPException, Query
from pydantic import BaseModel, Field

app = FastAPI(
    title="BookShelf App",
    description="A web application",
    version="1.0.0"
)


class Book(BaseModel):
    id: int
    title: str
    author: str
    pages: int = Field(ge=1)
    published_year: int = Field(ge=0)
    tags: List[str] = []


class BookCreate(BaseModel):
    title: str
    author: str
    pages: int = Field(ge=1)
    published_year: int = Field(ge=0)
    tags: List[str] = []


BOOKS: List[Book] = [
    Book(id=1, title="Clean Code", author="Robert C. Martin", pages=464, published_year=2008, tags=["software", "best-practices"]),
    Book(id=2, title="The Pragmatic Programmer", author="Andrew Hunt", pages=352, published_year=1999, tags=["software", "craftsmanship"]),
    Book(id=3, title="Deep Work", author="Cal Newport", pages=304, published_year=2016, tags=["productivity"]),
]


@app.get("/")
def read_root():
    return {"message": "Hello, Guys!"}


@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat() + "Z"}


@app.get("/echo")
def echo_message(message: str = Query(..., min_length=1, max_length=200)):
    return {"echo": message}

