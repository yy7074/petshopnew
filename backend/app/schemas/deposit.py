from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime
from typing import Optional, List

class DepositBase(BaseModel):
    amount: Decimal
    type: str
    description: Optional[str] = None
    auction_id: Optional[int] = None

class DepositCreate(DepositBase):
    payment_method: str = "balance"

class DepositResponse(DepositBase):
    id: int
    user_id: int
    status: str
    payment_method: str
    transaction_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    refunded_at: Optional[datetime]

    class Config:
        from_attributes = True

class DepositLogResponse(BaseModel):
    id: int
    deposit_id: int
    action: str
    amount: Decimal
    operator_id: Optional[int]
    reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class DepositSummaryResponse(BaseModel):
    """保证金汇总信息"""
    total_deposit: Decimal  # 总保证金
    active_deposit: Decimal  # 活跃保证金
    frozen_deposit: Decimal  # 冻结保证金
    available_for_refund: Decimal  # 可退还保证金

class DepositListResponse(BaseModel):
    items: List[DepositResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

class PayDepositRequest(BaseModel):
    amount: Decimal
    type: str = "general"  # general 或 auction
    auction_id: Optional[int] = None
    payment_method: str = "balance"  # balance 或 alipay
    description: Optional[str] = None

class RefundDepositRequest(BaseModel):
    deposit_id: int
    reason: Optional[str] = "用户申请退还"