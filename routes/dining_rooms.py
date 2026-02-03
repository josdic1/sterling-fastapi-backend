# routes/dining_rooms.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models.dining_room import DiningRoom
from schemas.dining_room import DiningRoomResponse

router = APIRouter()

@router.get("/", response_model=List[DiningRoomResponse])
@router.get("", response_model=List[DiningRoomResponse])
def get_dining_rooms(db: Session = Depends(get_db)):
    """Get all dining rooms (includes is_active field)"""
    rooms = db.query(DiningRoom).all()
    return rooms