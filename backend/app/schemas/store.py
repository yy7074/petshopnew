from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

class StoreBase(BaseModel):
    name: str
    description: Optional[str] = None
    avatar: Optional[str] = None
    banner: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    is_open: bool = True
    business_hours: Optional[Dict[str, Any]] = None
    announcement: Optional[str] = None

class StoreCreate(StoreBase):
    pass

class StoreUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    avatar: Optional[str] = None
    banner: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    is_open: Optional[bool] = None
    business_hours: Optional[Dict[str, Any]] = None
    announcement: Optional[str] = None

class StoreResponse(StoreBase):
    id: int
    owner_id: int
    total_products: int
    total_sales: int
    total_revenue: Decimal
    rating: Decimal
    rating_count: int
    follower_count: int
    status: int
    verified: bool
    created_at: datetime
    updated_at: datetime
    
    # 额外信息
    owner_info: Optional[Dict[str, Any]] = None
    is_following: bool = False
    recent_products: Optional[List[Dict[str, Any]]] = None

    class Config:
        from_attributes = True

class StoreListResponse(BaseModel):
    items: List[StoreResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

class StoreFollowRequest(BaseModel):
    store_id: int

class StoreReviewBase(BaseModel):
    store_id: int
    order_id: int
    rating: int  # 1-5
    comment: Optional[str] = None
    images: Optional[List[str]] = None

class StoreReviewCreate(StoreReviewBase):
    pass

class StoreReviewResponse(StoreReviewBase):
    id: int
    user_id: int
    reply: Optional[str] = None
    replied_at: Optional[datetime] = None
    status: int
    created_at: datetime
    updated_at: datetime
    
    user_info: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class StoreReviewListResponse(BaseModel):
    items: List[StoreReviewResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    # 统计信息
    rating_summary: Dict[str, int] = {}  # 各评分数量统计
    average_rating: float = 0.0

class StoreStatsResponse(BaseModel):
    """店铺统计信息"""
    total_products: int
    active_products: int
    total_orders: int
    total_revenue: Decimal
    total_reviews: int
    average_rating: float
    follower_count: int
    
    # 最近统计
    recent_orders: int  # 最近30天订单
    recent_revenue: Decimal  # 最近30天收入
    recent_reviews: int  # 最近30天评价