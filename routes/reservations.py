# routes/reservations.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.reservation import Reservation
from models.dining_room import DiningRoom
from models.member import Member
from models.reservation_attendee import ReservationAttendee
from models.rule import Rule
from models.fee import Fee
from schemas.reservation import (
    ReservationCreate,
    ReservationUpdate,
    ReservationResponse,
    ReservationDetailResponse
)
from utils.auth import get_current_user

router = APIRouter()


# ===============================
# CREATE RESERVATION
# ===============================

@router.post("", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED)
def create_reservation(
    reservation_in: ReservationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Lock dining room row to prevent race conditions
    dining_room = (
        db.query(DiningRoom)
        .filter(DiningRoom.id == reservation_in.dining_room_id)
        .with_for_update()
        .first()
    )

    if not dining_room:
        raise HTTPException(status_code=404, detail="Dining room not found")

    # Check for overlapping confirmed reservations
    existing = db.query(Reservation).filter(
        Reservation.dining_room_id == reservation_in.dining_room_id,
        Reservation.date == reservation_in.date,
        Reservation.status == "confirmed"
    ).all()

    for res in existing:
        if not (
            reservation_in.end_time <= res.start_time
            or reservation_in.start_time >= res.end_time
        ):
            raise HTTPException(
                status_code=409,
                detail="This time slot overlaps with an existing booking"
            )

    # Create reservation
    new_res = Reservation(
        created_by_id=current_user.id,
        dining_room_id=reservation_in.dining_room_id,
        date=reservation_in.date,
        meal_type=reservation_in.meal_type,
        start_time=reservation_in.start_time,
        end_time=reservation_in.end_time,
        notes=reservation_in.notes,
        status="confirmed"
    )

    db.add(new_res)
    db.commit()
    db.refresh(new_res)

    # Add creator as attendee if they have a member record
    creator_member = db.query(Member).filter(
        Member.user_id == current_user.id
    ).first()

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

    # Apply automatic fees
    apply_automatic_fees(db, new_res)

    attendee_count = db.query(ReservationAttendee).filter_by(
        reservation_id=new_res.id
    ).count()

    return ReservationResponse(
        id=new_res.id,
        created_by_id=new_res.created_by_id,
        dining_room_id=new_res.dining_room_id,
        date=new_res.date,
        meal_type=new_res.meal_type,
        start_time=new_res.start_time,
        end_time=new_res.end_time,
        notes=new_res.notes,
        status=new_res.status,
        created_at=new_res.created_at,
        attendee_count=attendee_count
    )


# ===============================
# LIST MY RESERVATIONS
# ===============================

@router.get("", response_model=list[ReservationResponse])
@router.get("/", response_model=list[ReservationResponse])
def get_my_reservations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    reservations = (
        db.query(Reservation)
        .filter(Reservation.created_by_id == current_user.id)
        .order_by(Reservation.date.desc())
        .all()
    )

    result = []
    for res in reservations:
        attendee_count = db.query(ReservationAttendee).filter_by(
            reservation_id=res.id
        ).count()

        result.append(
            ReservationResponse(
                id=res.id,
                created_by_id=res.created_by_id,
                dining_room_id=res.dining_room_id,
                date=res.date,
                meal_type=res.meal_type,
                start_time=res.start_time,
                end_time=res.end_time,
                notes=res.notes,
                status=res.status,
                created_at=res.created_at,
                attendee_count=attendee_count
            )
        )

    return result


# ===============================
# GET SINGLE RESERVATION
# ===============================

@router.get("/{reservation_id}", response_model=ReservationDetailResponse)
def get_reservation(
    reservation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    res = db.query(Reservation).filter(
        Reservation.id == reservation_id,
        Reservation.created_by_id == current_user.id
    ).first()

    if not res:
        raise HTTPException(status_code=404, detail="Reservation not found")

    return ReservationDetailResponse(
        id=res.id,
        created_by_id=res.created_by_id,
        dining_room_id=res.dining_room_id,
        date=res.date,
        meal_type=res.meal_type,
        start_time=res.start_time,
        end_time=res.end_time,
        notes=res.notes,
        status=res.status,
        created_at=res.created_at,
        dining_room={
            "id": res.dining_room.id,
            "name": res.dining_room.name,
            "capacity": res.dining_room.capacity
        }
    )


# ===============================
# UPDATE
# ===============================

@router.patch("/{reservation_id}", response_model=ReservationResponse)
def update_reservation(
    reservation_id: int,
    update: ReservationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    res = db.query(Reservation).filter(
        Reservation.id == reservation_id,
        Reservation.created_by_id == current_user.id
    ).first()

    if not res:
        raise HTTPException(status_code=404, detail="Not found")

    for key, value in update.model_dump(exclude_unset=True).items():
        setattr(res, key, value)

    db.commit()
    db.refresh(res)

    apply_automatic_fees(db, res)

    attendee_count = db.query(ReservationAttendee).filter_by(
        reservation_id=res.id
    ).count()

    return ReservationResponse(
        id=res.id,
        created_by_id=res.created_by_id,
        dining_room_id=res.dining_room_id,
        date=res.date,
        meal_type=res.meal_type,
        start_time=res.start_time,
        end_time=res.end_time,
        notes=res.notes,
        status=res.status,
        created_at=res.created_at,
        attendee_count=attendee_count
    )


# ===============================
# DELETE
# ===============================

@router.delete("/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reservation(
    reservation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    res = db.query(Reservation).filter(
        Reservation.id == reservation_id,
        Reservation.created_by_id == current_user.id
    ).first()

    if not res:
        raise HTTPException(status_code=404, detail="Not found")

    db.delete(res)
    db.commit()
    return None


# ===============================
# FEE AUTOMATION
# ===============================

def apply_automatic_fees(db: Session, reservation: Reservation):
    attendees = db.query(ReservationAttendee).filter_by(
        reservation_id=reservation.id
    ).all()

    total_count = len(attendees)
    member_attendees = [a for a in attendees if a.member_id is not None]
    guest_count = len([a for a in attendees if a.member_id is None])

    # PEAK HOURS
    peak_rule = db.query(Rule).filter_by(code="peak_hours", enabled=1).first()
    if peak_rule and reservation.date.weekday() in [4, 5, 6]:
        existing = db.query(Fee).filter_by(
            reservation_id=reservation.id,
            rule_id=peak_rule.id
        ).first()
        if not existing:
            db.add(Fee(
                reservation_id=reservation.id,
                rule_id=peak_rule.id,
                calculated_amount=peak_rule.base_amount,
                paid=0
            ))
    else:
        if peak_rule:
            existing = db.query(Fee).filter_by(
                reservation_id=reservation.id,
                rule_id=peak_rule.id
            ).first()
            if existing:
                db.delete(existing)

    db.commit()
