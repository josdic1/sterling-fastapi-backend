# models/fee.py
"""
Fee model - a rule applied to a specific reservation with calculated amount.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Fee(Base):
    __tablename__ = "fees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Foreign keys
    reservation_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("reservations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    rule_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("rules.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # Fee calculation
    quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    calculated_amount: Mapped[float] = mapped_column(Float, nullable=False)
    override_amount: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Payment status (store as 0/1 for cross-db stability)
    paid: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # Relationships
    reservation: Mapped["Reservation"] = relationship(  # type: ignore
        "Reservation",
        back_populates="fees",
    )
    rule: Mapped["Rule"] = relationship("Rule")  # type: ignore

    @property
    def final_amount(self) -> float:
        """Returns override_amount if set, otherwise calculated_amount"""
        return self.override_amount if self.override_amount is not None else self.calculated_amount

    @property
    def is_paid(self) -> bool:
        """Convenience boolean for API usage"""
        return self.paid == 1

    def __repr__(self) -> str:
        return (
            f"<Fee(id={self.id}, reservation={self.reservation_id}, "
            f"rule={self.rule_id}, amount=${self.final_amount}, paid={self.paid})>"
        )
