# models/dining_room.py
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class DiningRoom(Base):
    __tablename__ = "dining_rooms"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
