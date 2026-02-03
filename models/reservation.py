# models/reservation.py
"""
Reservation model - a booking for a dining room at a specific time.
"""
from __future__ import annotations

from datetime import datetime, timezone
from datetime import date as date_type
from datetime import time as time_type

from sqlalchemy import String, Integer, Text, Date, DateTime, Time, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.user import User
    from models.dining_room import DiningRoom
    from models.reservation_attendee import ReservationAttendee
    from models.fee import Fee


class Reservation(Base):
    __tablename__ = "reservations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Foreign keys
    created_by_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    dining_room_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("dining_rooms.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # Reservation details
    date: Mapped[date_type] = mapped_column(Date, nullable=False, index=True)
    meal_type: Mapped[str] = mapped_column(String(20), nullable=False)  # 'lunch' or 'dinner'
    start_time: Mapped[time_type] = mapped_column(Time, nullable=False)
    end_time: Mapped[time_type] = mapped_column(Time, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20),
        default="confirmed",
        nullable=False,
        index=True,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # Relationships
    created_by: Mapped["User"] = relationship("User", back_populates="reservations")  # type: ignore
    dining_room: Mapped["DiningRoom"] = relationship("DiningRoom")  # type: ignore
    attendees: Mapped[list["ReservationAttendee"]] = relationship(
        "ReservationAttendee",
        back_populates="reservation",
        cascade="all, delete-orphan",
    )  # type: ignore
    fees: Mapped[list["Fee"]] = relationship(
        "Fee",
        back_populates="reservation",
        cascade="all, delete-orphan",
    )  # type: ignore

    def __repr__(self) -> str:
        return (
            f"<Reservation(id={self.id}, room={self.dining_room_id}, date={self.date}, "
            f"meal={self.meal_type}, status={self.status})>"
        )
