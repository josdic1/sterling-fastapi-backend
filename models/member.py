# models/member.py
"""
Member model - individual person under a user account.
Users can have multiple members (family members, guests, etc.)
"""
from sqlalchemy import String, Integer, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class Member(Base):
    __tablename__ = "members"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Member details
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    relation: Mapped[str | None] = mapped_column(String(50), nullable=True)
    dietary_restrictions: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Relationship back to user
    # models/member.py
    user: Mapped["User"] = relationship("User", back_populates="members")  # type: ignore
    
    def __repr__(self) -> str:
        return f"<Member(id={self.id}, name={self.name}, user_id={self.user_id})>"