# schemas/fee.py
"""
Pydantic schemas for Fee
Expose paid as a boolean, while DB stores paid as 0/1 integer.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FeeCreate(BaseModel):
    """What the system/admin sends when applying a fee"""
    rule_id: int
    quantity: int | None = None
    calculated_amount: float
    override_amount: float | None = None
    # NOTE: we do NOT accept "paid" here from users for fee creation


class FeeUpdate(BaseModel):
    """What admin sends when updating a fee"""
    override_amount: float | None = None
    paid: bool | None = None


class FeeResponse(BaseModel):
    """What we send back to users"""
    id: int
    reservation_id: int
    rule_id: int
    quantity: int | None
    calculated_amount: float
    override_amount: float | None
    # IMPORTANT: read from Fee.is_paid property, but output as "paid"
    paid: bool = Field(validation_alias="is_paid")
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class FeeDetailResponse(BaseModel):
    """Detailed response with rule information"""
    id: int
    reservation_id: int
    quantity: int | None
    calculated_amount: float
    override_amount: float | None
    paid: bool = Field(validation_alias="is_paid")
    created_at: datetime

    # Nested rule info
    rule: dict  # {"id": 1, "code": "...", "name": "...", "base_amount": 40.0}

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
