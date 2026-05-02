from collections.abc import Generator

from sqlalchemy import create_engine
import os
from sqlalchemy.orm import Session, declarative_base, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"


def get_database_url() -> str:
    """Return `DATABASE_URL` when set, otherwise use the local SQLite default."""
    # Falling back to SQLite keeps a fresh checkout runnable.
    return os.environ.get("DATABASE_URL", SQLALCHEMY_DATABASE_URL)


def masked_database_url() -> str:
    """Return a masked/sanitized database URL for safe logging (hide credentials)."""
    url = get_database_url()
    try:
        # Expected form for non-sqlite URLs: scheme://user:pass@host/...
        if "@" in url and ":" in url.split("@")[0]:
            # mask user:pass portion
            head, tail = url.split("@", 1)
            if ":" in head:
                user, _ = head.split(":", 1)
                return f"{user}:*****@{tail}"
    except Exception:
        pass
    # Leave sqlite URLs unchanged so local paths stay readable.
    # SQLite URLs and malformed inputs fall back to the original value.
    return url

engine = create_engine(
    # Pull from env when present to keep local/prod config flexible.
    get_database_url(),
    # Needed for SQLite usage from FastAPI request threads.
    connect_args={"check_same_thread": False},
    # Pre-ping avoids stale pooled connections after DB restarts.
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    # Keep objects readable after commit without explicit refresh in some flows.
    expire_on_commit=False,
    # Reuse the shared engine so sessions are consistent across requests.
    bind=engine
)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Provide a transactional database session for each request."""
    # Session is scoped to a single request lifecycle.
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

