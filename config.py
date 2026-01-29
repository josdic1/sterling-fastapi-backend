# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./sterling.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60 * 24
    APP_TITLE: str = "Catering Booking API"
    APP_DESCRIPTION: str = "Book catering events with ease"
    APP_VERSION: str = "1.0.0"


# ← ADD THIS LINE (lowercase 'settings')
settings = Settings()