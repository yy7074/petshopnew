from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

class OrderBase(BaseModel):
    product_id: int
    quantity: int = 1
    order_type: str  # "auction" or "buy_now"
    payment_method: int  # 1:支付宝, 2:微信, 3:银行卡
    shipping_address: Dict[str, Any]
    buyer_note: Optional[str] = None

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    shipping_address: Optional[Dict[str, Any]] = None
    buyer_note: Optional[str] = None
    seller_note: Optional[str] = None

class OrderResponse(OrderBase):
    id: int
    order_no: str
    buyer_id: int
    seller_id: int
    final_price: Decimal
    shipping_fee: Decimal = Decimal('0.00')
    total_amount: Decimal
    payment_method: Optional[int] = None
    payment_status: int = 1  # 1:待支付,2:已支付,3:已退款
    order_status: int = 1    # 1:待支付,2:待发货,3:已发货,4:已收货,5:已完成,6:已取消
    shipping_address: Optional[Dict[str, Any]] = None
    tracking_number: Optional[str] = None
    shipped_at: Optional[datetime] = None
    received_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    items: List[Dict[str, Any]] = []
    buyer_info: Optional[Dict[str, Any]] = None
    seller_info: Optional[Dict[str, Any]] = None
    product_info: Optional[Dict[str, Any]] = None
    payment_info: Optional[Dict[str, Any]] = None
    logistics_info: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class OrderListResponse(BaseModel):
    items: List[OrderResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

class PaymentBase(BaseModel):
    order_id: int
    payment_method: int
    amount: Decimal

class PaymentCreate(PaymentBase):
    pass

class PaymentResponse(PaymentBase):
    id: int
    user_id: int
    status: str
    transaction_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class LogisticsResponse(BaseModel):
    order_id: int
    tracking_number: Optional[str] = None
    logistics_company: Optional[str] = None
    status: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class OrderStatistics(BaseModel):
    period: str
    buyer_stats: Dict[str, Any]
    seller_stats: Dict[str, Any]
    status_distribution: List[Dict[str, Any]]