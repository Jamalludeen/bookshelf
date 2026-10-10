from collections.abc import Generator

from sqlalchemy import create_engine
import os
from sqlalchemy.orm import Session, declarative_base, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"


def get_database_url() -> str:
    """Return `DATABASE_URL` when set, otherwise use the local SQLite default."""
    # Falling back to SQLite keeps a fresh checkout runnable.
    configured_url = os.environ.get("DATABASE_URL", "").strip()
    return configured_url or SQLALCHEMY_DATABASE_URL


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


def database_dialect() -> str:
    """Return the SQLAlchemy dialect name for the configured database."""
    return engine.dialect.name

DATABASE_URL = get_database_url()
engine_options = {
    "pool_pre_ping": True,
    "pool_recycle": 1800,
}
if DATABASE_URL.startswith("sqlite"):
    engine_options["connect_args"] = {"check_same_thread": False, "timeout": 10}

engine = create_engine(DATABASE_URL, **engine_options)

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
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
        