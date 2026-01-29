# routes/fees.py
"""
Fee routes - managing fees on reservations
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.reservation import Reservation
from models.fee import Fee
from models.rule import Rule
from schemas.fee import FeeCreate, FeeDetailResponse
from utils.auth import get_current_user

router = APIRouter()


@router.post("/{reservation_id}/fees", response_model=FeeDetailResponse, status_code=status.HTTP_201_CREATED)
def apply_fee(
    reservation_id: int,
    fee_in: FeeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Apply a fee to a reservation.
    User can apply fees to their own reservations.
    (In production, this might be admin-only or automatic)
    """
    # Verify reservation belongs to user
    reservation = db.query(Reservation).filter(
        Reservation.id == reservation_id,
        Reservation.created_by_id == current_user.id
    ).first()
    
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation not found"
        )
    
    # Verify rule exists
    rule = db.query(Rule).filter(Rule.id == fee_in.rule_id).first()
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rule not found"
        )
    
    # Check if fee already applied
    existing = db.query(Fee).filter(
        Fee.reservation_id == reservation_id,
        Fee.rule_id == fee_in.rule_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Fee '{rule.name}' already applied to this reservation"
        )
    
    # Create fee
    new_fee = Fee(
        reservation_id=reservation_id,
        rule_id=fee_in.rule_id,
        quantity=fee_in.quantity,
        calculated_amount=fee_in.calculated_amount,
        override_amount=fee_in.override_amount,
        paid=False
    )
    
    db.add(new_fee)
    db.commit()
    db.refresh(new_fee)
    
    # Return detailed response with rule info
    return {
        "id": new_fee.id,
        "reservation_id": new_fee.reservation_id,
        "quantity": new_fee.quantity,
        "calculated_amount": new_fee.calculated_amount,
        "override_amount": new_fee.override_amount,
        "paid": new_fee.paid,
        "created_at": new_fee.created_at,
        "rule": {
            "id": rule.id,
            "code": rule.code,
            "name": rule.name,
            "base_amount": rule.base_amount
        }
    }


@router.get("/{reservation_id}/fees", response_model=list[FeeDetailResponse])
def get_fees(
    reservation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all fees for a reservation.
    User can only view fees for their own reservations.
    """
    # Verify reservation belongs to user
    reservation = db.query(Reservation).filter(
        Reservation.id == reservation_id,
        Reservation.created_by_id == current_user.id
    ).first()
    
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation not found"
        )
    
    fees = db.query(Fee).filter(Fee.reservation_id == reservation_id).all()
    
    # Build detailed responses
    result = []
    for fee in fees:
        result.append({
            "id": fee.id,
            "reservation_id": fee.reservation_id,
            "quantity": fee.quantity,
            "calculated_amount": fee.calculated_amount,
            "override_amount": fee.override_amount,
            "paid": fee.paid,
            "created_at": fee.created_at,
            "rule": {
                "id": fee.rule.id,
                "code": fee.rule.code,
                "name": fee.rule.name,
                "base_amount": fee.rule.base_amount
            }
        })
    
    return result


@router.delete("/{reservation_id}/fees/{fee_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_fee(
    reservation_id: int,
    fee_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove a fee from a reservation.
    User can remove fees from their own reservations.
    """
    # Verify reservation belongs to user
    reservation = db.query(Reservation).filter(
        Reservation.id == reservation_id,
        Reservation.created_by_id == current_user.id
    ).first()
    
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation not found"
        )
    
    # Find and delete fee
    fee = db.query(Fee).filter(
        Fee.id == fee_id,
        Fee.reservation_id == reservation_id
    ).first()
    
    if not fee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fee not found"
        )
    
    db.delete(fee)
    db.commit()
    
    return None