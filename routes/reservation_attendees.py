# routes/reservation_attendees.py
"""
Reservation Attendee routes - managing who's coming to reservations
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.reservation import Reservation
from models.member import Member
from models.reservation_attendee import ReservationAttendee
from schemas.reservation_attendee import AttendeeCreate, AttendeeResponse
from utils.auth import get_current_user
from routes.reservations import apply_automatic_fees

router = APIRouter()


@router.post(
    "/{reservation_id}/attendees",
    response_model=AttendeeResponse,
    status_code=status.HTTP_201_CREATED,
)
@router.post(
    "/{reservation_id}/attendees/",
    response_model=AttendeeResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_attendee(
    reservation_id: int,
    attendee_in: AttendeeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Add an attendee to a reservation.
    User can only add attendees to their own reservations.
    """
    reservation = db.query(Reservation).filter(
        Reservation.id == reservation_id,
        Reservation.created_by_id == current_user.id,
    ).first()

    if not reservation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found")

    # Validate input - must provide either member_id OR name
    if not attendee_in.member_id and not attendee_in.name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Must provide either member_id or name")

    # Case 1: Adding a registered member
    if attendee_in.member_id:
        member = db.query(Member).filter(
            Member.id == attendee_in.member_id,
            Member.user_id == current_user.id,
        ).first()

        if not member:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

        existing = db.query(ReservationAttendee).filter(
            ReservationAttendee.reservation_id == reservation_id,
            ReservationAttendee.member_id == attendee_in.member_id,
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"{member.name} is already added to this reservation",
            )

        new_attendee = ReservationAttendee(
            reservation_id=reservation_id,
            member_id=member.id,
            name=member.name,
            attendee_type="member",
            dietary_restrictions=member.dietary_restrictions,
        )

    # Case 2: Adding a one-time guest
    else:
        new_attendee = ReservationAttendee(
            reservation_id=reservation_id,
            member_id=None,
            name=attendee_in.name,
            attendee_type="guest",
            dietary_restrictions=attendee_in.dietary_restrictions,
        )

    db.add(new_attendee)
    db.commit()
    db.refresh(new_attendee)

    # TRIGGER FEE RECALCULATION
    apply_automatic_fees(db, reservation)

    return new_attendee


@router.get(
    "/{reservation_id}/attendees",
    response_model=list[AttendeeResponse],
)
@router.get(
    "/{reservation_id}/attendees/",
    response_model=list[AttendeeResponse],
)
def get_attendees(
    reservation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all attendees for a reservation.
    User can only view attendees for their own reservations.
    """
    reservation = db.query(Reservation).filter(
        Reservation.id == reservation_id,
        Reservation.created_by_id == current_user.id,
    ).first()

    if not reservation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found")

    attendees = db.query(ReservationAttendee).filter(
        ReservationAttendee.reservation_id == reservation_id
    ).all()

    return attendees


@router.delete(
    "/{reservation_id}/attendees/{attendee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
@router.delete(
    "/{reservation_id}/attendees/{attendee_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_attendee(
    reservation_id: int,
    attendee_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Remove an attendee from a reservation.
    User can only remove attendees from their own reservations.
    """
    reservation = db.query(Reservation).filter(
        Reservation.id == reservation_id,
        Reservation.created_by_id == current_user.id,
    ).first()

    if not reservation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found")

    attendee = db.query(ReservationAttendee).filter(
        ReservationAttendee.id == attendee_id,
        ReservationAttendee.reservation_id == reservation_id,
    ).first()

    if not attendee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendee not found")

    db.delete(attendee)
    db.commit()

    # TRIGGER FEE RECALCULATION
    apply_automatic_fees(db, reservation)

    return None
