from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.db.models import Base

# Configure engine. For SQLite, need check_same_thread=False
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initializes tables on startup or import."""
    Base.metadata.create_all(bind=engine)


# Eagerly initialize schema for SQLite or local dev
try:
    init_db()
except Exception:
    pass


def get_db():
    """FastAPI dependency for obtaining a database session."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
