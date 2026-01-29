# schemas/reservation_attendee.py
"""
Pydantic schemas for Reservation Attendee
"""
from pydantic import BaseModel, ConfigDict


class AttendeeCreate(BaseModel):
    """
    What the user sends when adding an attendee.
    Either member_id (registered member) OR name (one-time guest).
    """
    member_id: int | None = None  # If adding a registered member
    name: str | None = None        # If adding a one-time guest
    dietary_restrictions: str | None = None  # Only for guests


class AttendeeResponse(BaseModel):
    """What we send back to the user"""
    id: int
    reservation_id: int
    member_id: int | None
    name: str
    attendee_type: str  # "member" or "guest"
    dietary_restrictions: str | None
    
    model_config = ConfigDict(from_attributes=True)