from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.member import Member
from schemas.member import MemberCreate, MemberUpdate, MemberResponse
from utils.auth import get_current_user

router = APIRouter()


@router.post("", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
def create_member(
    member_in: MemberCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
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


@router.get("", response_model=list[MemberResponse])
@router.get("/", response_model=list[MemberResponse])
def get_my_members(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Member).filter(Member.user_id == current_user.id).all()


@router.get("/{member_id}", response_model=MemberResponse)
def get_member(
    member_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    member = db.query(Member).filter(
        Member.id == member_id,
        Member.user_id == current_user.id
    ).first()

    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    return member


@router.patch("/{member_id}", response_model=MemberResponse)
def update_member(
    member_id: int,
    member_update: MemberUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    member = db.query(Member).filter(
        Member.id == member_id,
        Member.user_id == current_user.id
    ).first()

    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    for key, value in member_update.model_dump(exclude_unset=True).items():
        setattr(member, key, value)

    db.commit()
    db.refresh(member)
    return member


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(
    member_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    member = db.query(Member).filter(
        Member.id == member_id,
        Member.user_id == current_user.id
    ).first()

    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    db.delete(member)
    db.commit()
    return None
