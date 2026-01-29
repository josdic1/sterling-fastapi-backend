# models/reservation.py
"""
Reservation model - a booking for a dining room at a specific time.
"""
from sqlalchemy import String, Integer, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from datetime import date as date_type
from database import Base


class Reservation(Base):
    __tablename__ = "reservations"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    created_by_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    dining_room_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("dining_rooms.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    time_slot_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("time_slots.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    
    # Reservation details
    date: Mapped[date_type] = mapped_column(Date, nullable=False, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="confirmed", nullable=False, index=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )
    
    # Relationships
    created_by: Mapped["User"] = relationship("User", back_populates="reservations")  # type: ignore
    dining_room: Mapped["DiningRoom"] = relationship("DiningRoom")  # type: ignore
    time_slot: Mapped["TimeSlot"] = relationship("TimeSlot")  # type: ignore
    attendees: Mapped[list["ReservationAttendee"]] = relationship("ReservationAttendee", back_populates="reservation", cascade="all, delete-orphan")  # type: ignore
    fees: Mapped[list["Fee"]] = relationship("Fee", back_populates="reservation", cascade="all, delete-orphan")  # type: ignore
    
    def __repr__(self) -> str:
        return f"<Reservation(id={self.id}, room={self.dining_room_id}, date={self.date}, status={self.status})>"