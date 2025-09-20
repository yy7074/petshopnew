from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class LotteryPrizeBase(BaseModel):
    name: str
    type: str  # voucher/coupon/pet
    value: Optional[float] = None
    icon: Optional[str] = None
    color: str = "#FFD700"
    probability: float
    stock: int = -1
    description: Optional[str] = None
    sort_order: int = 0

class LotteryPrizeCreate(LotteryPrizeBase):
    pass

class LotteryPrizeUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    value: Optional[float] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    probability: Optional[float] = None
    stock: Optional[int] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None
    sort_order: Optional[int] = None

class LotteryPrize(LotteryPrizeBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class LotteryDrawRequest(BaseModel):
    pass  # 抽奖请求暂时不需要参数

class LotteryDrawResult(BaseModel):
    success: bool
    message: str
    prize: Optional[LotteryPrize] = None
    remaining_draws: int
    total_draws_today: int

class LotteryRecordResponse(BaseModel):
    id: int
    prize_name: str
    prize_type: str
    prize_value: Optional[float]
    is_claimed: bool
    claimed_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

class LotteryHistoryResponse(BaseModel):
    items: List[LotteryRecordResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

class LotteryConfigResponse(BaseModel):
    max_daily_draws: int
    cost_per_draw: int
    is_active: bool
    remaining_draws: int
    prizes: List[LotteryPrize]
    description: Optional[str] = None
