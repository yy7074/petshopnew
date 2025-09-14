from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# 管理员登录
class AdminLoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)

class AdminInfo(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    
    class Config:
        from_attributes = True

class AdminLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    admin_info: AdminInfo

class TokenVerifyResponse(BaseModel):
    valid: bool
    admin_info: Optional[AdminInfo] = None

# 仪表盘统计
class DashboardStats(BaseModel):
    total_users: int
    total_products: int
    today_orders: int
    today_revenue: float
    month_new_users: int
    month_revenue: float

# 用户管理
class UserInfo(BaseModel):
    id: int
    username: str
    phone: str
    email: Optional[str] = None
    nickname: Optional[str] = None
    is_seller: bool = False
    is_verified: bool = False
    balance: float = 0.0
    credit_score: int = 100
    status: int = 1
    last_login_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserListResponse(BaseModel):
    users: List[UserInfo]
    total: int
    page: int
    size: int

# 商品管理
class ProductInfo(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    starting_price: float
    current_price: float
    buy_now_price: Optional[float] = None
    auction_type: int = 1
    auction_start_time: Optional[datetime] = None
    auction_end_time: Optional[datetime] = None
    location: Optional[str] = None
    shipping_fee: float = 0.0
    is_free_shipping: bool = False
    condition_type: int = 1
    view_count: int = 0
    bid_count: int = 0
    favorite_count: int = 0
    status: int = 1
    is_featured: bool = False
    created_at: datetime
    seller_name: Optional[str] = None
    category_name: Optional[str] = None
    
    class Config:
        from_attributes = True

class ProductListResponse(BaseModel):
    products: List[ProductInfo]
    total: int
    page: int
    size: int

# 分类管理
class CategoryInfo(BaseModel):
    id: int
    name: str
    parent_id: int = 0
    icon_url: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True
    created_at: datetime
    parent_name: Optional[str] = None
    product_count: int = 0
    
    class Config:
        from_attributes = True

class CategoryListResponse(BaseModel):
    categories: List[CategoryInfo]

# 订单管理
class OrderInfo(BaseModel):
    id: int
    order_no: str
    final_price: float
    shipping_fee: float = 0.0
    total_amount: float
    payment_method: Optional[int] = None
    payment_status: int = 1
    order_status: int = 1
    tracking_number: Optional[str] = None
    shipped_at: Optional[datetime] = None
    received_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    buyer_name: Optional[str] = None
    product_title: Optional[str] = None
    
    class Config:
        from_attributes = True

class OrderListResponse(BaseModel):
    orders: List[OrderInfo]
    total: int
    page: int
    size: int

# 店铺管理
class ShopInfo(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    avatar: Optional[str] = None
    banner: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    is_open: bool = True
    verified: bool = False
    rating: float = 5.0
    total_sales: int = 0
    created_at: datetime
    owner_name: Optional[str] = None
    
    class Config:
        from_attributes = True

class ShopListResponse(BaseModel):
    shops: List[ShopInfo]
    total: int
    page: int
    size: int

# 专场活动管理
class EventInfo(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    banner_image: Optional[str] = None
    start_time: datetime
    end_time: datetime
    is_active: bool = True
    created_at: datetime
    product_count: Optional[int] = 0
    
    class Config:
        from_attributes = True

class EventListResponse(BaseModel):
    events: List[EventInfo]
    total: int
    page: int
    size: int

# 消息管理
class MessageInfo(BaseModel):
    id: int
    message_type: str = "text"
    title: Optional[str] = None
    content: str
    related_id: Optional[int] = None
    is_read: bool = False
    created_at: datetime
    sender_name: Optional[str] = None
    receiver_name: Optional[str] = None
    
    class Config:
        from_attributes = True

class MessageListResponse(BaseModel):
    messages: List[MessageInfo]
    total: int
    page: int
    size: int

class SystemMessageRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1, max_length=1000)
    receiver_type: str = Field(..., pattern="^(all|user)$")  # all: 全部用户, user: 指定用户
    receiver_ids: Optional[List[int]] = None  # 当receiver_type为user时必填

# 统计数据
class StatisticsOverview(BaseModel):
    daily_users: List[Dict[str, Any]]
    daily_orders: List[Dict[str, Any]]
    daily_revenue: List[Dict[str, Any]]

# 系统设置
class SystemSettingsRequest(BaseModel):
    site_name: Optional[str] = None
    site_description: Optional[str] = None
    contact_email: Optional[str] = None
    min_bid_amount: Optional[float] = None
    bid_increment: Optional[float] = None
    auction_duration: Optional[int] = None

class SystemSettingsResponse(BaseModel):
    site_name: str
    site_description: str
    contact_email: str
    min_bid_amount: float
    bid_increment: float
    auction_duration: int

# 批量操作
class BatchOperationRequest(BaseModel):
    ids: List[int]
    action: str  # enable, disable, delete, etc.
    
class BatchOperationResponse(BaseModel):
    success_count: int
    failure_count: int
    messages: List[str] = []