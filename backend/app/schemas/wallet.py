from pydantic import BaseModel
from decimal import Decimal
from typing import List, Optional
from datetime import datetime

class WalletResponse(BaseModel):
    balance: Decimal
    frozen_amount: Decimal = Decimal('0.00')
    total_recharge: Decimal = Decimal('0.00')
    total_consumption: Decimal = Decimal('0.00')

class RechargeRequest(BaseModel):
    amount: Decimal
    payment_method: str = "alipay"  # alipay, wechat, bank

class RechargeResponse(BaseModel):
    order_id: str
    payment_url: Optional[str] = None
    order_string: Optional[str] = None
    amount: Decimal
    status: str

class TransactionResponse(BaseModel):
    id: int
    type: str  # recharge, consumption, refund
    amount: Decimal
    balance_after: Decimal
    description: str
    status: str
    created_at: datetime

class TransactionListResponse(BaseModel):
    items: List[TransactionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
