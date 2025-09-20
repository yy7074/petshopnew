from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


# 用户基本信息
class UserBasic(BaseModel):
    id: int
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    is_verified: bool = False

    class Config:
        from_attributes = True


# 关注/粉丝用户信息
class FollowUser(BaseModel):
    id: int
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    description: Optional[str] = None
    follower_count: int = 0
    following_count: int = 0
    is_following: bool = False
    follow_time: Optional[datetime] = None
    last_active: Optional[str] = None
    is_verified: bool = False

    class Config:
        from_attributes = True


# 关注操作响应
class FollowResponse(BaseModel):
    success: bool
    message: str
    is_following: bool


# 关注列表响应
class FollowListResponse(BaseModel):
    items: List[FollowUser]
    total: int
    page: int
    page_size: int
    has_more: bool


# 浏览历史项
class BrowseHistoryItem(BaseModel):
    id: int
    product_id: int
    product_title: str
    product_image: Optional[str] = None
    product_price: str
    seller_name: str
    seller_location: str
    product_type: str  # auction, fixed
    product_status: str
    browse_time: datetime
    browse_time_text: str  # 相对时间文本

    class Config:
        from_attributes = True


# 浏览历史响应
class BrowseHistoryResponse(BaseModel):
    items: List[BrowseHistoryItem]
    total: int
    page: int
    page_size: int


# 用户信息更新请求
class UserInfoUpdate(BaseModel):
    nickname: Optional[str] = None
    real_name: Optional[str] = None
    gender: Optional[int] = None  # 0:未知,1:男,2:女
    birth_date: Optional[str] = None  # YYYY-MM-DD
    location: Optional[str] = None
    bio: Optional[str] = None
    email: Optional[str] = None


# 用户详细信息响应
class UserDetailResponse(BaseModel):
    id: int
    username: str
    nickname: Optional[str] = None
    real_name: Optional[str] = None
    phone: str
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    gender: int = 0
    birth_date: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    is_verified: bool = False
    follower_count: int = 0
    following_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True