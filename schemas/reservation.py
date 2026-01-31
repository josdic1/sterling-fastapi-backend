"""
Pydantic schemas for Reservation
"""
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from datetime import date as date_type
from datetime import time


class ReservationCreate(BaseModel):
    """What the user sends when creating a reservation"""
    dining_room_id: int
    date: date_type
    meal_type: str  # NEW - 'lunch' or 'dinner'
    start_time: time
    end_time: time
    notes: str | None = None


class ReservationUpdate(BaseModel):
    """What the user sends when updating a reservation"""
    dining_room_id: int | None = None
    date: date_type | None = None
    meal_type: str | None = None  # NEW
    start_time: time | None = None
    end_time: time | None = None
    notes: str | None = None
    status: str | None = None


class ReservationResponse(BaseModel):
    """What we send back to the user"""
    id: int
    created_by_id: int
    dining_room_id: int
    date: date_type
    meal_type: str  # NEW
    start_time: time
    end_time: time
    notes: str | None
    status: str
    created_at: datetime
    attendee_count: int = 0
    
    model_config = ConfigDict(from_attributes=True)


class ReservationDetailResponse(BaseModel):
    """Detailed response with nested objects"""
    id: int
    created_by_id: int
    dining_room_id: int
    date: date_type
    meal_type: str  # NEW
    start_time: time
    end_time: time
    notes: str | None
    status: str
    created_at: datetime
    
    # Nested objects
    dining_room: dict
    
    model_config = ConfigDict(from_attributes=True)