# models/dining_room.py
"""
Dining Room model - physical spaces where events are held.
These are static infrastructure - created by admin/seed only.
"""
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from database import Base


class DiningRoom(Base):
    __tablename__ = "dining_rooms"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    
    def __repr__(self) -> str:
        return f"<DiningRoom(id={self.id}, name={self.name}, capacity={self.capacity})>"