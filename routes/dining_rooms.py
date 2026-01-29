# routes/dining_rooms.py
"""
Dining Room routes - read-only for users
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.dining_room import DiningRoom
from schemas.dining_room import DiningRoomResponse  # ← Import from schemas

router = APIRouter()


@router.get("/", response_model=list[DiningRoomResponse])
def get_dining_rooms(db: Session = Depends(get_db)):
    """
    Get all dining rooms.
    Public endpoint - no authentication required.
    """
    rooms = db.query(DiningRoom).all()
    return rooms


