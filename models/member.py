"""
Member model - represents family members who can attend reservations.
"""
from sqlalchemy import String, Integer, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class Member(Base):
    __tablename__ = "members"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Member details
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    relation: Mapped[str | None] = mapped_column(String(50), nullable=True)
    dietary_restrictions: Mapped[str | None] = mapped_column(Text, nullable=True)
    guest_allowance: Mapped[int] = mapped_column(Integer, default=4, nullable=False)  # NEW
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="members")  # type: ignore
    reservation_attendees: Mapped[list["ReservationAttendee"]] = relationship("ReservationAttendee", back_populates="member")  # type: ignore
    
    def __repr__(self) -> str:
        return f"<Member(id={self.id}, name={self.name}, relation={self.relation})>"