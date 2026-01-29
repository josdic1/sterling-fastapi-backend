# schemas/fee.py
"""
Pydantic schemas for Fee
"""
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class FeeCreate(BaseModel):
    """What the system/admin sends when applying a fee"""
    rule_id: int
    quantity: int | None = None
    calculated_amount: float
    override_amount: float | None = None


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
    paid: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class FeeDetailResponse(BaseModel):
    """Detailed response with rule information"""
    id: int
    reservation_id: int
    quantity: int | None
    calculated_amount: float
    override_amount: float | None
    paid: bool
    created_at: datetime
    
    # Nested rule info
    rule: dict  # {"id": 1, "code": "no_call_no_show", "name": "No Call No Show Fee", "base_amount": 40.0}
    
    model_config = ConfigDict(from_attributes=True)