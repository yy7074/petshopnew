from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .product import ProductResponse, CategoryResponse

class SpecialEventResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    banner_image: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_active: bool = True
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class BannerResponse(BaseModel):
    id: int
    title: str
    image: str
    link: str
    sort_order: int = 1

    class Config:
        from_attributes = True

class HomeStatsResponse(BaseModel):
    total_products: int
    active_auctions: int
    active_events: int
    total_categories: int

class HomeDataResponse(BaseModel):
    hot_products: List[ProductResponse]
    recent_products: List[ProductResponse]
    recommended_products: List[ProductResponse]
    special_events: List[SpecialEventResponse]
    categories: List[CategoryResponse]

    class Config:
        from_attributes = True
