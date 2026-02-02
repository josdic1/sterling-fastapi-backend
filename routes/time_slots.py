from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.time_slot import TimeSlot
from schemas.time_slot import TimeSlotResponse

router = APIRouter()


@router.get("", response_model=list[TimeSlotResponse])
@router.get("/", response_model=list[TimeSlotResponse])
def get_time_slots(db: Session = Depends(get_db)):
    return db.query(TimeSlot).all()
