# routes/reservations.py
"""
Reservation routes - managing bookings
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.reservation import Reservation
from models.dining_room import DiningRoom
from models.time_slot import TimeSlot
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
    """
    Create a new reservation.
    Requires authentication.
    """
    # Validate dining room exists
    dining_room = db.query(DiningRoom).filter(DiningRoom.id == reservation_in.dining_room_id).first()
    if not dining_room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dining room not found"
        )
    
    # Validate time slot exists
    time_slot = db.query(TimeSlot).filter(TimeSlot.id == reservation_in.time_slot_id).first()
    if not time_slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time slot not found"
        )
    
    # Check for double booking (same room, same time slot, same date)
    existing = db.query(Reservation).filter(
        Reservation.dining_room_id == reservation_in.dining_room_id,
        Reservation.time_slot_id == reservation_in.time_slot_id,
        Reservation.date == reservation_in.date,
        Reservation.status == "confirmed"
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"This room is already booked for {time_slot.name} on {reservation_in.date}"
        )
    
    # Create reservation
    new_reservation = Reservation(
        created_by_id=current_user.id,
        dining_room_id=reservation_in.dining_room_id,
        time_slot_id=reservation_in.time_slot_id,
        date=reservation_in.date,
        notes=reservation_in.notes,
        status="confirmed"
    )
    
    db.add(new_reservation)
    db.commit()
    db.refresh(new_reservation)
    
    return new_reservation


@router.get("/", response_model=list[ReservationResponse])
def get_my_reservations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all reservations created by the current user.
    Requires authentication.
    """
    reservations = db.query(Reservation).filter(
        Reservation.created_by_id == current_user.id
    ).order_by(Reservation.date.desc()).all()
    
    return reservations


@router.get("/{reservation_id}", response_model=ReservationDetailResponse)
def get_reservation(
    reservation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific reservation with full details.
    User can only access their own reservations.
    """
    reservation = db.query(Reservation).filter(
        Reservation.id == reservation_id,
        Reservation.created_by_id == current_user.id
    ).first()
    
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation not found"
        )
    
    # Build detailed response with nested objects
    return {
        "id": reservation.id,
        "created_by_id": reservation.created_by_id,
        "date": reservation.date,
        "notes": reservation.notes,
        "status": reservation.status,
        "created_at": reservation.created_at,
        "dining_room": {
            "id": reservation.dining_room.id,
            "name": reservation.dining_room.name,
            "capacity": reservation.dining_room.capacity
        },
        "time_slot": {
            "id": reservation.time_slot.id,
            "name": reservation.time_slot.name,
            "start_time": reservation.time_slot.start_time.isoformat(),
            "end_time": reservation.time_slot.end_time.isoformat()
        }
    }


@router.patch("/{reservation_id}", response_model=ReservationResponse)
def update_reservation(
    reservation_id: int,
    reservation_update: ReservationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a reservation.
    User can only update their own reservations.
    """
    reservation = db.query(Reservation).filter(
        Reservation.id == reservation_id,
        Reservation.created_by_id == current_user.id
    ).first()
    
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation not found"
        )
    
    # Update fields
    if reservation_update.dining_room_id is not None:
        reservation.dining_room_id = reservation_update.dining_room_id
    if reservation_update.time_slot_id is not None:
        reservation.time_slot_id = reservation_update.time_slot_id
    if reservation_update.date is not None:
        reservation.date = reservation_update.date
    if reservation_update.notes is not None:
        reservation.notes = reservation_update.notes
    if reservation_update.status is not None:
        reservation.status = reservation_update.status
    
    db.commit()
    db.refresh(reservation)
    
    return reservation


@router.delete("/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reservation(
    reservation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete (cancel) a reservation.
    User can only delete their own reservations.
    """
    reservation = db.query(Reservation).filter(
        Reservation.id == reservation_id,
        Reservation.created_by_id == current_user.id
    ).first()
    
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation not found"
        )
    
    db.delete(reservation)
    db.commit()
    
    return None