from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

# ------- Pydantic Schemas (requests/responses) -------

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=80)
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserPublic(BaseModel):
    id: str
    name: str
    email: EmailStr
    avatar_url: Optional[str] = None
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=80)
    # email updates typically require re-verification; keeping immutable for now

# ------- Internal model shapes for Mongo -------

class UserInDB(BaseModel):
    name: str
    email: EmailStr
    password_hash: str
    avatar_url: Optional[str] = None
    created_at: datetime

    class Config:
        arbitrary_types_allowed = True
