# schemas/dining_room.py
"""
Pydantic schemas for Dining Room
"""
from pydantic import BaseModel, ConfigDict


class DiningRoomResponse(BaseModel):
    """What we send back to users"""
    id: int
    name: str
    capacity: int
    
    model_config = ConfigDict(from_attributes=True)