# schemas/reservation.py
"""
Pydantic schemas for Reservation
"""
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from datetime import date as date_type


class ReservationCreate(BaseModel):
    """What the user sends when creating a reservation"""
    dining_room_id: int
    time_slot_id: int
    date: date_type
    notes: str | None = None


class ReservationUpdate(BaseModel):
    """What the user sends when updating a reservation"""
    dining_room_id: int | None = None
    time_slot_id: int | None = None
    date: date_type | None = None
    notes: str | None = None
    status: str | None = None


class ReservationResponse(BaseModel):
    """What we send back to the user"""
    id: int
    created_by_id: int
    dining_room_id: int
    time_slot_id: int
    date: date_type
    notes: str | None
    status: str
    created_at: datetime
    attendee_count: int = 0  # ← ADDED THIS
    
    model_config = ConfigDict(from_attributes=True)


class ReservationDetailResponse(BaseModel):
    """Detailed response with nested objects"""
    id: int
    created_by_id: int
    dining_room_id: int
    time_slot_id: int
    date: date_type
    notes: str | None
    status: str
    created_at: datetime
    
    # Nested objects
    dining_room: dict
    time_slot: dict
    
    model_config = ConfigDict(from_attributes=True)