# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from config import settings  # ← Import settings from config

# Use settings.DATABASE_URL (from .env file)
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}  # ← Needed for SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()