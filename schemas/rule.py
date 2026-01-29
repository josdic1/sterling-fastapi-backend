# schemas/rule.py
"""
Pydantic schemas for Rule
"""
from pydantic import BaseModel, ConfigDict


class RuleCreate(BaseModel):
    """What admin sends when creating a rule"""
    code: str
    name: str
    description: str | None = None
    fee_type: str  # "flat", "per_person", "percentage"
    base_amount: float
    threshold: int | None = None


class RuleUpdate(BaseModel):
    """What admin sends when updating a rule"""
    code: str | None = None
    name: str | None = None
    description: str | None = None
    fee_type: str | None = None
    base_amount: float | None = None
    threshold: int | None = None
    enabled: bool | None = None


class RuleResponse(BaseModel):
    """What we send back to users"""
    id: int
    code: str
    name: str
    description: str | None
    fee_type: str
    base_amount: float
    threshold: int | None
    enabled: bool
    
    model_config = ConfigDict(from_attributes=True)