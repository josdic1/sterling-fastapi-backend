# schemas/fee.py
"""
Pydantic schemas for Fee.

DB stores Fee.paid as 0/1 int for cross-db stability.
API exposes `paid` as a boolean (mapped from Fee.is_paid property).
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FeeCreate(BaseModel):
    """What the system/admin sends when applying a fee"""
    rule_id: int
    quantity: int | None = None
    calculated_amount: float
    override_amount: float | None = None
    # Do not accept paid on create


class FeeUpdate(BaseModel):
    """What admin sends when updating a fee"""
    override_amount: float | None = None
    paid: bool | None = None  # incoming boolean


class FeeResponse(BaseModel):
    """What we send back to users"""
    id: int
    reservation_id: int
    rule_id: int
    quantity: int | None
    calculated_amount: float
    override_amount: float | None
    paid: bool = Field(serialization_alias="paid", validation_alias="is_paid")
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class FeeDetailResponse(BaseModel):
    """Detailed response with rule information"""
    id: int
    reservation_id: int
    quantity: int | None
    calculated_amount: float
    override_amount: float | None
    paid: bool = Field(serialization_alias="paid", validation_alias="is_paid")
    created_at: datetime

    # Nested rule info
    rule: dict  # {"id": 1, "code": "...", "name": "...", "base_amount": 40.0}

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
