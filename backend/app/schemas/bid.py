from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class BidBase(BaseModel):
    product_id: int
    amount: Decimal

class BidCreate(BidBase):
    pass

class BidResponse(BidBase):
    id: int
    user_id: int
    is_auto_bid: bool
    status: int
    created_at: datetime
    user_info: Optional[dict] = None
    product_info: Optional[dict] = None

    class Config:
        from_attributes = True

class BidListResponse(BaseModel):
    items: List[BidResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

class AutoBidCreate(BaseModel):
    product_id: int
    max_amount: Decimal
    increment_amount: Decimal = Decimal('1.00')

class AutoBidResponse(BaseModel):
    id: int
    product_id: int
    user_id: int
    max_amount: Decimal
    increment_amount: Decimal
    status: str
    created_at: datetime
    product_title: Optional[str] = None

class BidStatistics(BaseModel):
    total_bids: int
    won_auctions: int
    winning_auctions: int
    total_amount: Decimal
    average_amount: Decimal
    success_rate: float