# config.py
import os
from dotenv import load_dotenv

load_dotenv()  # local only, harmless in Railway


class Settings:
    DATABASE_URL: str = os.environ["DATABASE_URL"]
    SECRET_KEY: str = os.environ["SECRET_KEY"]

    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60 * 24

    APP_TITLE: str = "Catering Booking API"
    APP_DESCRIPTION: str = "Book catering events with ease"
    APP_VERSION: str = "1.0.0"


settings = Settings()
