# models/time_slot.py
"""
Time Slot model - recurring time blocks for reservations.
These are static infrastructure - created by admin/seed only.
"""
from sqlalchemy import String, Integer, Time
from sqlalchemy.orm import Mapped, mapped_column
from datetime import time
from database import Base


class TimeSlot(Base):
    __tablename__ = "time_slots"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    
    def __repr__(self) -> str:
        return f"<TimeSlot(id={self.id}, name={self.name}, {self.start_time}-{self.end_time})>"