# utils/admin_auth.py
"""
Admin authentication utilities
Middleware to protect admin-only routes
"""
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from utils.auth import get_current_user


def get_admin_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to verify current user is an admin.
    Raises 403 if user is not admin.
    
    Usage in routes:
        @router.get("/admin/users")
        def get_all_users(admin: User = Depends(get_admin_user)):
            ...
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return current_user