from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.reservation import Reservation
from models.dining_room import DiningRoom
from models.time_slot import TimeSlot
from models.member import Member
from models.reservation_attendee import ReservationAttendee
from schemas.reservation import (
    ReservationCreate,
    ReservationUpdate,
    ReservationResponse,
    ReservationDetailResponse
)
from utils.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED)
def create_reservation(
    reservation_in: ReservationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Validations
    dining_room = db.query(DiningRoom).filter(DiningRoom.id == reservation_in.dining_room_id).first()
    if not dining_room:
        raise HTTPException(status_code=404, detail="Dining room not found")
    
    time_slot = db.query(TimeSlot).filter(TimeSlot.id == reservation_in.time_slot_id).first()
    if not time_slot:
        raise HTTPException(status_code=404, detail="Time slot not found")
    
    existing = db.query(Reservation).filter(
        Reservation.dining_room_id == reservation_in.dining_room_id,
        Reservation.time_slot_id == reservation_in.time_slot_id,
        Reservation.date == reservation_in.date,
        Reservation.status == "confirmed"
    ).first()
    
    if existing:
        raise HTTPException(status_code=409, detail="This slot is already booked")

    # 2. Create Reservation
    new_res = Reservation(
        created_by_id=current_user.id,
        dining_room_id=reservation_in.dining_room_id,
        time_slot_id=reservation_in.time_slot_id,
        date=reservation_in.date,
        notes=reservation_in.notes,
        status="confirmed"
    )
    db.add(new_res)
    db.commit()
    db.refresh(new_res)

    # 3. AUTO-ADD THE USER AS THE FIRST ATTENDEE
    # We find the member record linked to this login so they aren't "blank"
    creator_member = db.query(Member).filter(Member.user_id == current_user.id).first()
    if creator_member:
        attendee = ReservationAttendee(
            reservation_id=new_res.id,
            member_id=creator_member.id,
            name=creator_member.name,
            attendee_type="member",
            dietary_restrictions=creator_member.dietary_restrictions
        )
        db.add(attendee)
        db.commit()

    return new_res

@router.get("/", response_model=list[ReservationResponse])
def get_my_reservations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Reservation).filter(Reservation.created_by_id == current_user.id).order_by(Reservation.date.desc()).all()

@router.get("/{reservation_id}", response_model=ReservationDetailResponse)
def get_reservation(reservation_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    res = db.query(Reservation).filter(Reservation.id == reservation_id, Reservation.created_by_id == current_user.id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    return {
        "id": res.id,
        "created_by_id": res.created_by_id,
        "dining_room_id": res.dining_room_id,  # ← ADD THIS
        "time_slot_id": res.time_slot_id,      # ← ADD THIS
        "date": res.date,
        "notes": res.notes,
        "status": res.status,
        "created_at": res.created_at,
        "dining_room": {"id": res.dining_room.id, "name": res.dining_room.name, "capacity": res.dining_room.capacity},
        "time_slot": {
            "id": res.time_slot.id, 
            "name": res.time_slot.name, 
            "start_time": res.time_slot.start_time.isoformat(), 
            "end_time": res.time_slot.end_time.isoformat()
        }
    }

@router.patch("/{reservation_id}", response_model=ReservationResponse)
def update_reservation(reservation_id: int, update: ReservationUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    res = db.query(Reservation).filter(Reservation.id == reservation_id, Reservation.created_by_id == current_user.id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Not found")
    
    # Standard update logic
    for key, value in update.model_dump(exclude_unset=True).items():
        setattr(res, key, value)
    
    db.commit()
    db.refresh(res)
    return res

@router.delete("/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reservation(reservation_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    res = db.query(Reservation).filter(Reservation.id == reservation_id, Reservation.created_by_id == current_user.id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(res)
    db.commit()
    return None