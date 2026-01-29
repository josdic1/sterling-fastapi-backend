# models/rule.py
"""
Rule model - defines fee templates (no-call-no-show, peak hours, etc.)
These are created by admins and applied to reservations as fees.
"""
from sqlalchemy import String, Integer, Float, Text
from sqlalchemy.orm import Mapped, mapped_column
from database import Base


class Rule(Base):
    __tablename__ = "rules"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Rule identification
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Fee calculation
    fee_type: Mapped[str] = mapped_column(String(20), nullable=False)  # "flat", "per_person", "percentage"
    base_amount: Mapped[float] = mapped_column(Float, nullable=False)
    threshold: Mapped[int | None] = mapped_column(Integer, nullable=True)  # e.g., "applies when party > 6"
    
    # Status
    enabled: Mapped[bool] = mapped_column(Integer, default=True, nullable=False)  # SQLite uses Integer for Boolean
    
    def __repr__(self) -> str:
        return f"<Rule(id={self.id}, code={self.code}, name={self.name})>"