from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ServiceStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

# 宠物交流相关
class PetSocialPostCreate(BaseModel):
    title: str = Field(..., max_length=200)
    content: str
    images: Optional[List[str]] = None
    pet_type: Optional[str] = Field(None, max_length=50)
    location: Optional[str] = Field(None, max_length=200)

class PetSocialPostUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    images: Optional[List[str]] = None
    pet_type: Optional[str] = Field(None, max_length=50)
    location: Optional[str] = Field(None, max_length=200)

class PetSocialCommentCreate(BaseModel):
    content: str
    parent_id: Optional[int] = None

class PetSocialCommentResponse(BaseModel):
    id: int
    content: str
    parent_id: Optional[int]
    user_id: int
    user_nickname: Optional[str]
    user_avatar: Optional[str] = None
    created_at: datetime
    replies: List['PetSocialCommentResponse'] = []

    class Config:
        from_attributes = True

class PetSocialPostResponse(BaseModel):
    id: int
    title: str
    content: str
    images: Optional[List[str]]
    pet_type: Optional[str]
    location: Optional[str]
    view_count: int
    like_count: int
    comment_count: int
    is_top: bool
    status: ServiceStatus
    user_id: int
    user_nickname: Optional[str]
    user_avatar: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class PetSocialPostListResponse(BaseModel):
    items: List[PetSocialPostResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

# 宠物配种相关
class PetBreedingInfoCreate(BaseModel):
    pet_name: str = Field(..., max_length=100)
    pet_type: str = Field(..., max_length=50)
    breed: str = Field(..., max_length=100)
    gender: str = Field(..., max_length=10)
    age: int = Field(..., gt=0)
    weight: Optional[float] = Field(None, gt=0)
    health_status: Optional[str] = Field(None, max_length=200)
    vaccination_status: Optional[str] = Field(None, max_length=200)
    images: Optional[List[str]] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    location: str = Field(..., max_length=200)
    contact_phone: Optional[str] = Field(None, max_length=20)
    contact_wechat: Optional[str] = Field(None, max_length=50)
    price: Optional[float] = Field(None, ge=0)

class PetBreedingInfoUpdate(BaseModel):
    pet_name: Optional[str] = Field(None, max_length=100)
    pet_type: Optional[str] = Field(None, max_length=50)
    breed: Optional[str] = Field(None, max_length=100)
    gender: Optional[str] = Field(None, max_length=10)
    age: Optional[int] = Field(None, gt=0)
    weight: Optional[float] = Field(None, gt=0)
    health_status: Optional[str] = Field(None, max_length=200)
    vaccination_status: Optional[str] = Field(None, max_length=200)
    images: Optional[List[str]] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    location: Optional[str] = Field(None, max_length=200)
    contact_phone: Optional[str] = Field(None, max_length=20)
    contact_wechat: Optional[str] = Field(None, max_length=50)
    price: Optional[float] = Field(None, ge=0)
    is_available: Optional[bool] = None

class PetBreedingInfoResponse(BaseModel):
    id: int
    pet_name: str
    pet_type: str
    breed: str
    gender: str
    age: int
    weight: Optional[float]
    health_status: Optional[str]
    vaccination_status: Optional[str]
    images: Optional[List[str]]
    description: Optional[str]
    requirements: Optional[str]
    location: str
    contact_phone: Optional[str]
    contact_wechat: Optional[str]
    price: Optional[float]
    is_available: bool
    status: ServiceStatus
    user_id: int
    user_nickname: Optional[str]
    user_avatar: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class PetBreedingInfoListResponse(BaseModel):
    items: List[PetBreedingInfoResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

# 本地宠店相关
class LocalPetStoreCreate(BaseModel):
    name: str = Field(..., max_length=200)
    owner_name: Optional[str] = Field(None, max_length=100)
    phone: str = Field(..., max_length=20)
    address: str = Field(..., max_length=500)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    business_hours: Optional[str] = Field(None, max_length=200)
    services: Optional[List[str]] = None
    images: Optional[List[str]] = None
    description: Optional[str] = None

class LocalPetStoreUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    owner_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    business_hours: Optional[str] = Field(None, max_length=200)
    services: Optional[List[str]] = None
    images: Optional[List[str]] = None
    description: Optional[str] = None

class LocalPetStoreResponse(BaseModel):
    id: int
    name: str
    owner_name: Optional[str]
    phone: str
    address: str
    latitude: Optional[float]
    longitude: Optional[float]
    business_hours: Optional[str]
    services: Optional[List[str]]
    images: Optional[List[str]]
    description: Optional[str]
    rating: float
    review_count: int
    is_verified: bool
    status: ServiceStatus
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class LocalPetStoreListResponse(BaseModel):
    items: List[LocalPetStoreResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

# 鱼缸造景相关
class AquariumDesignServiceCreate(BaseModel):
    title: str = Field(..., max_length=200)
    description: str
    tank_sizes: Optional[List[str]] = None
    design_styles: Optional[List[str]] = None
    price_range: Optional[str] = Field(None, max_length=100)
    portfolio_images: Optional[List[str]] = None
    location: str = Field(..., max_length=200)
    contact_phone: Optional[str] = Field(None, max_length=20)
    contact_wechat: Optional[str] = Field(None, max_length=50)

class AquariumDesignServiceUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    tank_sizes: Optional[List[str]] = None
    design_styles: Optional[List[str]] = None
    price_range: Optional[str] = Field(None, max_length=100)
    portfolio_images: Optional[List[str]] = None
    location: Optional[str] = Field(None, max_length=200)
    contact_phone: Optional[str] = Field(None, max_length=20)
    contact_wechat: Optional[str] = Field(None, max_length=50)
    is_available: Optional[bool] = None

class AquariumDesignServiceResponse(BaseModel):
    id: int
    title: str
    description: str
    tank_sizes: Optional[List[str]]
    design_styles: Optional[List[str]]
    price_range: Optional[str]
    portfolio_images: Optional[List[str]]
    location: str
    contact_phone: Optional[str]
    contact_wechat: Optional[str]
    rating: float
    order_count: int
    is_available: bool
    status: ServiceStatus
    provider_id: int
    provider_nickname: Optional[str]
    provider_avatar: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class AquariumDesignServiceListResponse(BaseModel):
    items: List[AquariumDesignServiceResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

# 上门服务相关
class DoorServiceCreate(BaseModel):
    service_name: str = Field(..., max_length=200)
    service_type: str = Field(..., max_length=100)
    description: str
    service_area: str = Field(..., max_length=200)
    price: float = Field(..., gt=0)
    duration: Optional[int] = Field(None, gt=0)
    equipment_needed: Optional[str] = None
    images: Optional[List[str]] = None
    contact_phone: str = Field(..., max_length=20)

class DoorServiceUpdate(BaseModel):
    service_name: Optional[str] = Field(None, max_length=200)
    service_type: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    service_area: Optional[str] = Field(None, max_length=200)
    price: Optional[float] = Field(None, gt=0)
    duration: Optional[int] = Field(None, gt=0)
    equipment_needed: Optional[str] = None
    images: Optional[List[str]] = None
    contact_phone: Optional[str] = Field(None, max_length=20)
    is_available: Optional[bool] = None

class DoorServiceResponse(BaseModel):
    id: int
    service_name: str
    service_type: str
    description: str
    service_area: str
    price: float
    duration: Optional[int]
    equipment_needed: Optional[str]
    images: Optional[List[str]]
    contact_phone: str
    rating: float
    order_count: int
    is_available: bool
    status: ServiceStatus
    provider_id: int
    provider_nickname: Optional[str]
    provider_avatar: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class DoorServiceListResponse(BaseModel):
    items: List[DoorServiceResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

# 宠物估价相关
class PetValuationServiceCreate(BaseModel):
    pet_type: str = Field(..., max_length=50)
    breed: str = Field(..., max_length=100)
    age: int = Field(..., gt=0)
    gender: str = Field(..., max_length=10)
    weight: Optional[float] = Field(None, gt=0)
    health_status: Optional[str] = Field(None, max_length=200)
    special_features: Optional[str] = None
    images: List[str] = Field(..., min_items=1)

class PetValuationServiceResponse(BaseModel):
    id: int
    pet_type: str
    breed: str
    age: int
    gender: str
    weight: Optional[float]
    health_status: Optional[str]
    special_features: Optional[str]
    images: List[str]
    estimated_value: Optional[float]
    valuator_id: Optional[int]
    valuator_nickname: Optional[str]
    valuation_notes: Optional[str]
    status: ServiceStatus
    user_id: int
    user_nickname: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class PetValuationServiceListResponse(BaseModel):
    items: List[PetValuationServiceResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

# 附近发现相关
class NearbyItemCreate(BaseModel):
    title: str = Field(..., max_length=200)
    description: str
    category: str = Field(..., max_length=50)
    price: Optional[float] = Field(None, ge=0)
    images: Optional[List[str]] = None
    location: str = Field(..., max_length=200)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    contact_phone: Optional[str] = Field(None, max_length=20)
    contact_wechat: Optional[str] = Field(None, max_length=50)

class NearbyItemUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50)
    price: Optional[float] = Field(None, ge=0)
    images: Optional[List[str]] = None
    location: Optional[str] = Field(None, max_length=200)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    contact_phone: Optional[str] = Field(None, max_length=20)
    contact_wechat: Optional[str] = Field(None, max_length=50)

class NearbyItemResponse(BaseModel):
    id: int
    title: str
    description: str
    category: str
    price: Optional[float]
    images: Optional[List[str]]
    location: str
    latitude: Optional[float]
    longitude: Optional[float]
    contact_phone: Optional[str]
    contact_wechat: Optional[str]
    view_count: int
    like_count: int
    is_top: bool
    status: ServiceStatus
    user_id: int
    user_nickname: Optional[str]
    user_avatar: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class NearbyItemListResponse(BaseModel):
    items: List[NearbyItemResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

# 通用响应
class ServiceStatsResponse(BaseModel):
    total_posts: int
    total_breeding: int
    total_stores: int
    total_designs: int
    total_door_services: int
    total_valuations: int
    total_nearby_items: int

# 更新PetSocialCommentResponse的前向引用
PetSocialCommentResponse.model_rebuild()

