# routes/fees.py
"""
Fee calculation and management routes
"""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models.reservation import Reservation
from models.reservation_attendee import ReservationAttendee
from models.rule import Rule
from models.fee import Fee
from schemas.fee import FeeDetailResponse
from utils.auth import get_current_user
from models.user import User

router = APIRouter()


@router.get("/{reservation_id}/fees", response_model=List[FeeDetailResponse])
@router.get("/{reservation_id}/fees/", response_model=List[FeeDetailResponse])
def calculate_fees(
    reservation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Calculate all applicable fees for a reservation.
    Returns fees with embedded rule so frontend can display fee.rule.name.
    """
    try:
        reservation = (
            db.query(Reservation)
            .filter(Reservation.id == reservation_id)
            .first()
        )
        if not reservation:
            raise HTTPException(status_code=404, detail="Reservation not found")

        # Clear existing fees
        db.query(Fee).filter(Fee.reservation_id == reservation_id).delete()
        db.commit()

        attendees = (
            db.query(ReservationAttendee)
            .filter(ReservationAttendee.reservation_id == reservation_id)
            .all()
        )
        if not attendees:
            return []

        total_party = len(attendees)
        members_count = sum(1 for a in attendees if a.attendee_type == "member")
        guests_count = sum(1 for a in attendees if a.attendee_type == "guest")

        # Active rules
        rules = db.query(Rule).filter(Rule.enabled == 1).all()
        rules_by_code = {r.code: r for r in rules}

        # === 1) EXCESS MEMBER GUESTS ===
        if "excess_member_guests" in rules_by_code:
            rule = rules_by_code["excess_member_guests"]
            allowed_guests = members_count * 4
            excess_guests = max(0, guests_count - allowed_guests)

            if excess_guests > 0:
                fee_amount = excess_guests * rule.base_amount
                db.add(
                    Fee(
                        reservation_id=reservation_id,
                        rule_id=rule.id,
                        quantity=excess_guests,
                        calculated_amount=fee_amount,
                        paid=0,
                    )
                )

        # === 2) EXCESS OCCUPANCY ===
        if "excess_occupancy" in rules_by_code:
            rule = rules_by_code["excess_occupancy"]
            threshold = rule.threshold if rule.threshold is not None else 12

            if total_party > threshold:
                excess = total_party - threshold
                fee_amount = excess * rule.base_amount
                db.add(
                    Fee(
                        reservation_id=reservation_id,
                        rule_id=rule.id,
                        quantity=excess,
                        calculated_amount=fee_amount,
                        paid=0,
                    )
                )

        # === 3) PEAK HOURS ===
        if "peak_hours" in rules_by_code:
            rule = rules_by_code["peak_hours"]
            # weekday(): Mon=0 ... Sun=6; Fri=4, Sat=5, Sun=6
            is_weekend = reservation.date.weekday() >= 4
            if is_weekend:
                db.add(
                    Fee(
                        reservation_id=reservation_id,
                        rule_id=rule.id,
                        quantity=None,
                        calculated_amount=rule.base_amount,
                        paid=0,
                    )
                )

        db.commit()

        # Return the persisted fees WITH their rule loaded
        fees = (
            db.query(Fee)
            .options(joinedload(Fee.rule))
            .filter(Fee.reservation_id == reservation_id)
            .all()
        )
        return fees

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Fee calculation failed: {str(e)}")
