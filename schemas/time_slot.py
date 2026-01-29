# schemas/time_slot.py
"""
Pydantic schemas for Time Slot
"""
from pydantic import BaseModel, ConfigDict
from datetime import time


class TimeSlotResponse(BaseModel):
    """What we send back to users"""
    id: int
    name: str
    start_time: time
    end_time: time
    
    model_config = ConfigDict(from_attributes=True)