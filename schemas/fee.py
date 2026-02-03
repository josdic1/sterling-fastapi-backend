# schemas/fee.py
"""
Pydantic schemas for Fee.

DB stores Fee.paid as 0/1 int for cross-db stability.
API exposes `paid` as a boolean via Fee.is_paid property.
Also embeds the related Rule so frontend can render fee.rule.name.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class RuleMini(BaseModel):
    """Embedded rule fields needed by frontend."""
    id: int
    code: str
    name: str
    description: Optional[str] = None
    fee_type: Optional[str] = None
    base_amount: float
    threshold: Optional[int] = None
    enabled: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class FeeCreate(BaseModel):
    rule_id: int
    quantity: Optional[int] = None
    calculated_amount: float
    override_amount: Optional[float] = None
    # do not accept paid on create


class FeeUpdate(BaseModel):
    override_amount: Optional[float] = None
    paid: Optional[bool] = None  # incoming boolean


class FeeResponse(BaseModel):
    """Basic fee response (no embedded rule)."""
    id: int
    reservation_id: int
    rule_id: int
    quantity: Optional[int] = None
    calculated_amount: float
    override_amount: Optional[float] = None
    paid: bool = Field(validation_alias="is_paid")
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class FeeDetailResponse(BaseModel):
    """Fee response WITH embedded rule for UI."""
    id: int
    reservation_id: int
    rule_id: int
    quantity: Optional[int] = None
    calculated_amount: float
    override_amount: Optional[float] = None
    paid: bool = Field(validation_alias="is_paid")
    created_at: datetime

    rule: RuleMini

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
