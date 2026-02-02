from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.rule import Rule
from schemas.rule import RuleResponse

router = APIRouter()


@router.get("", response_model=list[RuleResponse])
@router.get("/", response_model=list[RuleResponse])
def get_rules(db: Session = Depends(get_db)):
    rules = db.query(Rule).filter(Rule.enabled == 1).all()
    return rules


@router.get("/{rule_id}", response_model=RuleResponse)
def get_rule(rule_id: int, db: Session = Depends(get_db)):
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule