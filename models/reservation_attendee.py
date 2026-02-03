# models/reservation_attendee.py
"""
Reservation Attendee model - tracks who is attending a reservation.
Can be either a registered member OR a one-time guest.
"""
from sqlalchemy import String, Integer, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class ReservationAttendee(Base):
    __tablename__ = "reservation_attendees"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # on foreign soil

    # Foreign keys
    reservation_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("reservations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    ok = ""
    # Optional - if this is a registered member
    member_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("members.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Required - name (from member OR guest)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Attendee type: "member" or "guest"
    attendee_type: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Dietary restrictions - only for guests
    # Members inherit from members table
    dietary_restrictions: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Relationships
    reservation: Mapped["Reservation"] = relationship("Reservation", back_populates="attendees")  # type: ignore
    member: Mapped["Member | None"] = relationship("Member")  # type: ignore
    
    def __repr__(self) -> str:
        return f"<ReservationAttendee(id={self.id}, name={self.name}, type={self.attendee_type})>"