# schemas/member.py
"""
Pydantic schemas for Member
"""
from pydantic import BaseModel, ConfigDict


class MemberCreate(BaseModel):
    """What the user sends when creating a member"""
    name: str
    relation: str | None = None
    dietary_restrictions: str | None = None


class MemberUpdate(BaseModel):
    """What the user sends when updating a member"""
    name: str | None = None
    relation: str | None = None
    dietary_restrictions: str | None = None


class MemberResponse(BaseModel):
    """What we send back to the user"""
    id: int
    user_id: int
    name: str
    relation: str | None
    dietary_restrictions: str | None
    
    model_config = ConfigDict(from_attributes=True)