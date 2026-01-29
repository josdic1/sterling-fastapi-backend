# routes/rules.py
"""
Rule routes - fee templates (admin creates, users view)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.rule import Rule
from schemas.rule import RuleCreate, RuleUpdate, RuleResponse

router = APIRouter()


@router.get("/", response_model=list[RuleResponse])
def get_rules(db: Session = Depends(get_db)):
    """
    Get all fee rules.
    Public endpoint - users need to see what fees might apply.
    """
    rules = db.query(Rule).filter(Rule.enabled == True).all()
    return rules


@router.get("/{rule_id}", response_model=RuleResponse)
def get_rule(rule_id: int, db: Session = Depends(get_db)):
    """Get a specific rule by ID"""
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rule not found"
        )
    
    return rule


# Admin endpoints would go here (create, update, delete rules)
# For now, rules are created via seed script