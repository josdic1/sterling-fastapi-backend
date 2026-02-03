# routes/fees.py
"""
Fee calculation and management routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from database import get_db
from models.reservation import Reservation
from models.reservation_attendee import ReservationAttendee
from models.member import Member
from models.rule import Rule
from models.fee import Fee
from schemas.fee import FeeResponse
from utils.auth import get_current_user
from models.user import User

router = APIRouter()


@router.get("/{reservation_id}/fees", response_model=List[FeeResponse])
@router.get("/{reservation_id}/fees/", response_model=List[FeeResponse])
def calculate_fees(
    reservation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Calculate all applicable fees for a reservation
    
    UPDATED LOGIC:
    - Count MEMBERS (attendee_type='member')
    - Count GUESTS (attendee_type='guest')  
    - Each member gets 4 guest allowance
    - Charge $15 for each guest beyond (members * 4)
    - Also charge $15 per person if total party > 12
    """
    reservation = db.query(Reservation).filter(
        Reservation.id == reservation_id
    ).first()
    
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    # Clear existing fees
    db.query(Fee).filter(Fee.reservation_id == reservation_id).delete()
    db.commit()
    
    # Get all attendees
    attendees = db.query(ReservationAttendee).filter(
        ReservationAttendee.reservation_id == reservation_id
    ).all()
    
    total_party = len(attendees)
    
    # UPDATED: Count members vs guests
    members_count = sum(1 for a in attendees if a.attendee_type == "member")
    guests_count = sum(1 for a in attendees if a.attendee_type == "guest")
    
    # Get active rules
    rules = db.query(Rule).filter(Rule.enabled == True).all()
    rules_by_code = {r.code: r for r in rules}
    
    fees = []
    
    # === EXCESS MEMBER GUESTS FEE ===
    # Formula: guests_count - (members_count * 4)
    if "excess_member_guests" in rules_by_code:
        rule = rules_by_code["excess_member_guests"]
        allowed_guests = members_count * 4
        excess_guests = max(0, guests_count - allowed_guests)
        
        if excess_guests > 0:
            fee_amount = excess_guests * rule.base_amount
            fee = Fee(
                reservation_id=reservation_id,
                rule_id=rule.id,
                calculated_amount=fee_amount,
                paid=False
            )
            db.add(fee)
            fees.append(fee)
    
    # === EXCESS OCCUPANCY FEE ===
    if "excess_occupancy" in rules_by_code:
        rule = rules_by_code["excess_occupancy"]
        # FIXED: Handle None threshold with proper type checking
        threshold = rule.threshold if rule.threshold is not None else 12
        
        if total_party > threshold:
            excess = total_party - threshold
            fee_amount = excess * rule.base_amount
            fee = Fee(
                reservation_id=reservation_id,
                rule_id=rule.id,
                calculated_amount=fee_amount,
                paid=False
            )
            db.add(fee)
            fees.append(fee)
    
    # === PEAK HOURS FEE ===
    if "peak_hours" in rules_by_code:
        rule = rules_by_code["peak_hours"]
        # Friday=4, Saturday=5, Sunday=6
        is_weekend = reservation.date.weekday() >= 4
        
        if is_weekend:
            fee = Fee(
                reservation_id=reservation_id,
                rule_id=rule.id,
                calculated_amount=rule.base_amount,
                paid=False
            )
            db.add(fee)
            fees.append(fee)
    
    db.commit()
    
    # Refresh and return
    for fee in fees:
        db.refresh(fee)
    
    return fees