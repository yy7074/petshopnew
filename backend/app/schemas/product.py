from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal

class CategoryResponse(BaseModel):
    id: int
    name: str
    parent_id: int
    icon_url: Optional[str] = None
    sort_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    title: str
    description: Optional[str] = None
    category_id: int
    starting_price: Decimal
    buy_now_price: Optional[Decimal] = None
    auction_type: int = 1
    auction_start_time: Optional[datetime] = None
    auction_end_time: Optional[datetime] = None
    location: Optional[str] = None
    shipping_fee: Decimal = Decimal('0.00')
    is_free_shipping: bool = False
    condition_type: int = 1
    stock_quantity: int = 1

class ProductCreate(ProductBase):
    images: Optional[List[str]] = []

class ProductUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    starting_price: Optional[Decimal] = None
    buy_now_price: Optional[Decimal] = None
    auction_type: Optional[int] = None
    auction_start_time: Optional[datetime] = None
    auction_end_time: Optional[datetime] = None
    location: Optional[str] = None
    shipping_fee: Optional[Decimal] = None
    is_free_shipping: Optional[bool] = None
    condition_type: Optional[int] = None
    stock_quantity: Optional[int] = None
    images: Optional[List[str]] = None

class ProductResponse(ProductBase):
    id: int
    seller_id: int
    current_price: Decimal
    view_count: int
    bid_count: int
    favorite_count: int
    status: int
    is_featured: bool
    images: Optional[List[str]] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProductDetailResponse(ProductResponse):
    is_favorited: bool = False
    seller_info: Optional[dict] = None

class ProductListResponse(BaseModel):
    items: List[ProductResponse]
    total: int
    page: int
    page_size: int
    total_pages: int