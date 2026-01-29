# routes/members.py
"""
Member routes - managing members under a user account
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.member import Member
from schemas.member import MemberCreate, MemberUpdate, MemberResponse
from utils.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
def create_member(
    member_in: MemberCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new member under the current user's account."""
    new_member = Member(
        user_id=current_user.id,
        name=member_in.name,
        relation=member_in.relation,
        dietary_restrictions=member_in.dietary_restrictions
    )
    
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    
    return new_member


@router.get("/", response_model=list[MemberResponse])
def get_my_members(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all members belonging to the current user."""
    members = db.query(Member).filter(Member.user_id == current_user.id).all()
    return members


@router.get("/{member_id}", response_model=MemberResponse)
def get_member(
    member_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific member by ID."""
    member = db.query(Member).filter(
        Member.id == member_id,
        Member.user_id == current_user.id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    return member


@router.patch("/{member_id}", response_model=MemberResponse)
def update_member(
    member_id: int,
    member_update: MemberUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a member's information."""
    member = db.query(Member).filter(
        Member.id == member_id,
        Member.user_id == current_user.id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    if member_update.name is not None:
        member.name = member_update.name
    if member_update.relation is not None:
        member.relation = member_update.relation
    if member_update.dietary_restrictions is not None:
        member.dietary_restrictions = member_update.dietary_restrictions
    
    db.commit()
    db.refresh(member)
    
    return member


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(
    member_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a member."""
    member = db.query(Member).filter(
        Member.id == member_id,
        Member.user_id == current_user.id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    db.delete(member)
    db.commit()
    
    return None