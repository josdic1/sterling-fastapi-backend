# schemas/dining_room.py
from pydantic import BaseModel

class DiningRoomResponse(BaseModel):
    """Schema for dining room responses"""
    id: int
    name: str
    capacity: int
    is_active: bool  # CRITICAL: Must include this field
    
    class Config:
        from_attributes = True