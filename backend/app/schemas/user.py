from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, date
from decimal import Decimal

class UserBase(BaseModel):
    username: str
    phone: str
    email: Optional[EmailStr] = None
    nickname: Optional[str] = None
    real_name: Optional[str] = None
    gender: Optional[int] = 0
    birth_date: Optional[date] = None
    location: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    real_name: Optional[str] = None
    gender: Optional[int] = None
    birth_date: Optional[date] = None
    location: Optional[str] = None
    avatar_url: Optional[str] = None

class UserResponse(UserBase):
    id: int
    avatar_url: Optional[str] = None
    is_seller: bool = False
    is_verified: bool = False
    balance: Decimal = Decimal('0.00')
    credit_score: int = 100
    status: int = 1
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserAddressBase(BaseModel):
    receiver_name: str
    phone: str
    province: str
    city: str
    district: str
    detail_address: str
    postal_code: Optional[str] = None
    is_default: bool = False

class UserAddressCreate(UserAddressBase):
    pass

class UserAddressUpdate(BaseModel):
    receiver_name: Optional[str] = None
    phone: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    detail_address: Optional[str] = None
    postal_code: Optional[str] = None
    is_default: Optional[bool] = None

class UserAddressResponse(UserAddressBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
