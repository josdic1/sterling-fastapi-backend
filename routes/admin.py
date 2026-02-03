# routes/admin.py
"""
Admin-only routes for system management
All routes require admin authentication
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from database import get_db
from models.user import User
from models.member import Member
from models.reservation import Reservation
from models.reservation_attendee import ReservationAttendee
from models.dining_room import DiningRoom
from models.rule import Rule
from models.fee import Fee
from schemas.user import UserResponse
from schemas.member import MemberResponse
from schemas.reservation import ReservationResponse
from schemas.dining_room import DiningRoomResponse
from schemas.rule import RuleResponse, RuleUpdate
from utils.admin_auth import get_admin_user
from pydantic import BaseModel

router = APIRouter()


# ==================== SCHEMAS ====================

class DiningRoomUpdate(BaseModel):
    """Admin can update room capacity and availability"""
    capacity: int | None = None
    is_active: bool | None = None


class AdminStats(BaseModel):
    """Dashboard statistics"""
    total_users: int
    total_reservations: int
    total_members: int
    active_reservations: int
    total_revenue: float


# ==================== DASHBOARD STATS ====================

@router.get("/stats", response_model=AdminStats)
@router.get("/stats/", response_model=AdminStats)
def get_admin_stats(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics"""
    total_users = db.query(User).count()
    total_reservations = db.query(Reservation).count()
    total_members = db.query(Member).count()
    
    active_reservations = db.query(Reservation).filter(
        Reservation.status == "confirmed"
    ).count()
    
    # Calculate total revenue from fees
    total_revenue = db.query(func.sum(Fee.calculated_amount)).scalar() or 0.0
    
    return {
        "total_users": total_users,
        "total_reservations": total_reservations,
        "total_members": total_members,
        "active_reservations": active_reservations,
        "total_revenue": float(total_revenue)
    }


# ==================== VIEW ALL DATA ====================

@router.get("/users", response_model=List[UserResponse])
@router.get("/users/", response_model=List[UserResponse])
def get_all_users(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get all users in system"""
    users = db.query(User).order_by(User.created_at.desc()).all()
    return users


@router.get("/reservations", response_model=List[ReservationResponse])
@router.get("/reservations/", response_model=List[ReservationResponse])
def get_all_reservations(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
    status: str | None = None,
    room_id: int | None = None
):
    """
    Get all reservations across all users with optional filters
    
    Query params:
    - status: Filter by reservation status (confirmed, cancelled, etc.)
    - room_id: Filter by dining room
    """
    query = db.query(Reservation)
    
    if status:
        query = query.filter(Reservation.status == status)
    
    if room_id:
        query = query.filter(Reservation.dining_room_id == room_id)
    
    reservations = query.order_by(Reservation.date.desc()).all()
    
    # Add attendee count to each reservation
    result = []
    for res in reservations:
        attendee_count = db.query(ReservationAttendee).filter_by(
            reservation_id=res.id
        ).count()
        
        result.append(ReservationResponse(
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
        ))
    
    return result


@router.get("/members", response_model=List[MemberResponse])
@router.get("/members/", response_model=List[MemberResponse])
def get_all_members(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get all family members across all users"""
    members = db.query(Member).order_by(Member.name).all()
    return members


# ==================== FEE RULES MANAGEMENT ====================

@router.get("/rules", response_model=List[RuleResponse])
@router.get("/rules/", response_model=List[RuleResponse])
def get_all_rules_admin(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get all fee rules (including disabled ones)"""
    rules = db.query(Rule).order_by(Rule.id).all()
    return rules


@router.patch("/rules/{rule_id}", response_model=RuleResponse)
@router.patch("/rules/{rule_id}/", response_model=RuleResponse)
def update_rule(
    rule_id: int,
    rule_update: RuleUpdate,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Update fee rule (amount, threshold, enabled status)"""
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    # Update only provided fields
    for key, value in rule_update.model_dump(exclude_unset=True).items():
        setattr(rule, key, value)
    
    db.commit()
    db.refresh(rule)
    
    return rule


# ==================== DINING ROOM MANAGEMENT ====================

@router.patch("/dining-rooms/{room_id}", response_model=DiningRoomResponse)
@router.patch("/dining-rooms/{room_id}/", response_model=DiningRoomResponse)
def update_dining_room(
    room_id: int,
    room_update: DiningRoomUpdate,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Update dining room capacity or availability"""
    room = db.query(DiningRoom).filter(DiningRoom.id == room_id).first()
    
    if not room:
        raise HTTPException(status_code=404, detail="Dining room not found")
    
    # Update capacity
    if room_update.capacity is not None:
        if room_update.capacity < 1:
            raise HTTPException(
                status_code=400,
                detail="Capacity must be at least 1"
            )
        room.capacity = room_update.capacity
    
    # Update availability
    if room_update.is_active is not None:
        room.is_active = room_update.is_active
    
    db.commit()
    db.refresh(room)
    
    return room


# ==================== ADMIN OVERRIDES ====================

@router.delete("/reservations/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
@router.delete("/reservations/{reservation_id}/", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_reservation(
    reservation_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Admin can delete ANY reservation"""
    reservation = db.query(Reservation).filter(
        Reservation.id == reservation_id
    ).first()
    
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    db.delete(reservation)
    db.commit()
    
    return None


@router.delete("/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
@router.delete("/members/{member_id}/", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_member(
    member_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Admin can delete ANY member"""
    member = db.query(Member).filter(Member.id == member_id).first()
    
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    db.delete(member)
    db.commit()
    
    return None