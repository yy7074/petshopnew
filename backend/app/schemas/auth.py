from pydantic import BaseModel, EmailStr
from typing import Optional
from .user import UserResponse

class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    phone: str
    email: Optional[EmailStr] = None
    password: str
    nickname: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    user_id: Optional[int] = None
