from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from decimal import Decimal
from datetime import datetime

class SearchResponse(BaseModel):
    """搜索响应模型"""
    products: List[Dict[str, Any]] = []
    stores: List[Dict[str, Any]] = []
    total_products: int = 0
    total_stores: int = 0
    page: int = 1
    per_page: int = 20
    total_pages: int = 0
    has_more: bool = False

class SearchSuggestionResponse(BaseModel):
    """搜索建议响应模型"""
    suggestions: List[str] = []
    related_keywords: List[str] = []

class HotSearchResponse(BaseModel):
    """热门搜索响应模型"""
    hot_keywords: List[str] = []
    trending_products: List[Dict[str, Any]] = []
    popular_categories: List[Dict[str, Any]] = []

class SearchRequest(BaseModel):
    """搜索请求模型"""
    keyword: str
    category_id: Optional[int] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    sort_by: Optional[str] = "relevance"  # relevance, price_asc, price_desc, time_desc
    page: int = 1
    per_page: int = 20

class ProductSearchResult(BaseModel):
    """商品搜索结果模型"""
    id: int
    title: str
    description: Optional[str] = None
    current_price: Decimal
    reserve_price: Optional[Decimal] = None
    image_url: Optional[str] = None
    seller_name: str
    bid_count: int = 0
    end_time: Optional[datetime] = None
    status: str
    category_name: Optional[str] = None

class StoreSearchResult(BaseModel):
    """店铺搜索结果模型"""
    id: int
    name: str
    description: Optional[str] = None
    avatar_url: Optional[str] = None
    product_count: int = 0
    rating: Optional[float] = None
    location: Optional[str] = None
    is_verified: bool = False
