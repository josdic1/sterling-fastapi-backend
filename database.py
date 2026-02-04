# database.py
import time

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from config import settings

DATABASE_URL = settings.DATABASE_URL

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
else:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,   # detect dead connections before use
        pool_recycle=300,     # refresh connections periodically (seconds)
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
    )

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        # Postgres only: quick retry to survive DB restarts/recovery on Railway
        if not DATABASE_URL.startswith("sqlite"):
            for attempt in range(5):
                try:
                    db.execute(text("SELECT 1"))
                    break
                except OperationalError:
                    if attempt == 4:
                        raise
                    time.sleep(1)

        yield db
    finally:
        db.close()
