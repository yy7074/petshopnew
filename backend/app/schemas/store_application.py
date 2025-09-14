from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
import re

class StoreApplicationBase(BaseModel):
    store_name: str
    store_description: Optional[str] = None
    store_type: str
    consignee_name: str
    consignee_phone: str
    return_region: str
    return_address: str
    real_name: str
    id_number: str
    id_start_date: str
    id_end_date: str
    id_front_image: Optional[str] = None
    id_back_image: Optional[str] = None
    business_license_image: Optional[str] = None

    @validator('store_type')
    def validate_store_type(cls, v):
        allowed_types = ['个人店', '个体商家', '企业店', '旗舰店']
        if v not in allowed_types:
            raise ValueError(f'店铺类型必须是以下之一: {", ".join(allowed_types)}')
        return v

    @validator('consignee_phone')
    def validate_phone(cls, v):
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('请输入正确的手机号码')
        return v

    @validator('id_number')
    def validate_id_number(cls, v):
        if not re.match(r'^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[0-9Xx]$', v):
            raise ValueError('请输入正确的身份证号码')
        return v

class StoreApplicationCreate(StoreApplicationBase):
    pass

class StoreApplicationUpdate(BaseModel):
    store_name: Optional[str] = None
    store_description: Optional[str] = None
    store_type: Optional[str] = None
    consignee_name: Optional[str] = None
    consignee_phone: Optional[str] = None
    return_region: Optional[str] = None
    return_address: Optional[str] = None
    real_name: Optional[str] = None
    id_number: Optional[str] = None
    id_start_date: Optional[str] = None
    id_end_date: Optional[str] = None
    id_front_image: Optional[str] = None
    id_back_image: Optional[str] = None
    business_license_image: Optional[str] = None

class StoreApplicationResponse(StoreApplicationBase):
    id: int
    user_id: int
    status: int
    reject_reason: Optional[str] = None
    reviewer_id: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    deposit_amount: Decimal
    annual_fee: Decimal
    payment_status: int
    paid_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class StoreApplicationListResponse(BaseModel):
    items: List[StoreApplicationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

class StoreApplicationReview(BaseModel):
    status: int  # 1:通过, 2:拒绝
    reject_reason: Optional[str] = None

    @validator('status')
    def validate_status(cls, v):
        if v not in [1, 2]:
            raise ValueError('状态必须是1(通过)或2(拒绝)')
        return v

    @validator('reject_reason')
    def validate_reject_reason(cls, v, values):
        if values.get('status') == 2 and not v:
            raise ValueError('拒绝申请时必须提供拒绝原因')
        return v

class StoreTypeInfo(BaseModel):
    """店铺类型信息"""
    type_name: str
    deposit_amount: Decimal
    description: str

class StoreTypesResponse(BaseModel):
    """店铺类型列表响应"""
    types: List[StoreTypeInfo]
