from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime


# What the user sends when registering
class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str

# What we send back to the user (Safe - no password!)
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    name: str
    is_admin: bool
    created_at: datetime

    # Tells Pydantic to read SQLAlchemy models as dicts
    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    """What the user sends when logging in"""
    email: EmailStr
    password: str


# NEW: Login response (with token)
class TokenResponse(BaseModel):
    """What we send back after successful login"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse  # Include user info too