from collections.abc import Generator

from sqlalchemy import create_engine
import os
from sqlalchemy.orm import Session, declarative_base, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"


def get_database_url() -> str:
    """Return database URL from env `DATABASE_URL` or fallback to the default."""
    return os.environ.get("DATABASE_URL", SQLALCHEMY_DATABASE_URL)


def masked_database_url() -> str:
    """Return a masked/sanitized database URL for safe logging (hide credentials)."""
    url = get_database_url()
    try:
        if "@" in url and ":" in url.split("@")[0]:
            # mask user:pass portion
            head, tail = url.split("@", 1)
            if ":" in head:
                user, _ = head.split(":", 1)
                return f"{user}:*****@{tail}"
    except Exception:
        pass
    return url

engine = create_engine(
    # Pull from env when present to keep local/prod config flexible.
    get_database_url(),
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine
)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Provide a transactional database session for each request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

