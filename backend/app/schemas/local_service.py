from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal


class LocalServiceBase(BaseModel):
    service_type: str
    title: str
    description: Optional[str] = None
    content: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    price: Optional[Decimal] = None
    price_unit: Optional[str] = "元"
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_wechat: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None
    images: Optional[List[str]] = None
    tags: Optional[List[str]] = None


class LocalServiceCreate(LocalServiceBase):
    pass


class LocalServiceUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    price: Optional[Decimal] = None
    price_unit: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_wechat: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None
    images: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    status: Optional[int] = None


class LocalServiceResponse(LocalServiceBase):
    id: int
    user_id: int
    status: int
    is_featured: bool
    view_count: int
    like_count: int
    comment_count: int
    created_at: datetime
    updated_at: datetime
    
    # 用户信息
    user_info: Optional[Dict[str, Any]] = None
    
    # 是否已点赞/收藏（需要登录用户）
    is_liked: Optional[bool] = None
    is_favorited: Optional[bool] = None

    class Config:
        from_attributes = True


class LocalServiceListResponse(BaseModel):
    items: List[LocalServiceResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class LocalServiceCommentBase(BaseModel):
    content: str
    images: Optional[List[str]] = None
    parent_id: Optional[int] = None


class LocalServiceCommentCreate(LocalServiceCommentBase):
    pass


class LocalServiceCommentResponse(LocalServiceCommentBase):
    id: int
    service_id: int
    user_id: int
    status: int
    like_count: int
    created_at: datetime
    updated_at: datetime
    
    # 用户信息
    user_info: Optional[Dict[str, Any]] = None
    
    # 回复列表
    replies: Optional[List['LocalServiceCommentResponse']] = None

    class Config:
        from_attributes = True


class PetSocialPostBase(BaseModel):
    title: str
    content: str
    images: Optional[List[str]] = None
    pet_type: Optional[str] = None
    pet_breed: Optional[str] = None
    pet_age: Optional[str] = None
    pet_gender: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None


class PetSocialPostCreate(PetSocialPostBase):
    pass


class PetSocialPostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    images: Optional[List[str]] = None
    pet_type: Optional[str] = None
    pet_breed: Optional[str] = None
    pet_age: Optional[str] = None
    pet_gender: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[int] = None


class PetSocialPostResponse(PetSocialPostBase):
    id: int
    user_id: int
    view_count: int
    like_count: int
    comment_count: int
    share_count: int
    status: int
    is_top: bool
    is_featured: bool
    created_at: datetime
    updated_at: datetime
    
    # 用户信息
    user_info: Optional[Dict[str, Any]] = None
    
    # 是否已点赞
    is_liked: Optional[bool] = None

    class Config:
        from_attributes = True


class PetSocialPostListResponse(BaseModel):
    items: List[PetSocialPostResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class PetSocialCommentBase(BaseModel):
    content: str
    images: Optional[List[str]] = None
    parent_id: Optional[int] = None


class PetSocialCommentCreate(PetSocialCommentBase):
    pass


class PetSocialCommentResponse(PetSocialCommentBase):
    id: int
    post_id: int
    user_id: int
    status: int
    like_count: int
    created_at: datetime
    updated_at: datetime
    
    # 用户信息
    user_info: Optional[Dict[str, Any]] = None
    
    # 回复列表
    replies: Optional[List['PetSocialCommentResponse']] = None

    class Config:
        from_attributes = True


# 服务类型枚举
class ServiceType(BaseModel):
    key: str
    name: str
    description: str


class ServiceTypesResponse(BaseModel):
    items: List[ServiceType]


# 更新前向引用
LocalServiceCommentResponse.model_rebuild()
PetSocialCommentResponse.model_rebuild()
