from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.dining_room import DiningRoom
from schemas.dining_room import DiningRoomResponse

router = APIRouter()


@router.get("", response_model=list[DiningRoomResponse])
@router.get("/", response_model=list[DiningRoomResponse])
def get_dining_rooms(db: Session = Depends(get_db)):
    return db.query(DiningRoom).all()
