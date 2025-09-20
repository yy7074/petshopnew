from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List


class DailyReward(BaseModel):
    points: int
    description: str


class MilestoneInfo(BaseModel):
    days: int
    remaining_days: int
    reward: DailyReward


class CheckinStatus(BaseModel):
    is_checked_today: bool
    consecutive_days: int
    total_checkin_days: int
    month_checkin_dates: List[int]
    today_reward: DailyReward
    next_milestone: Optional[MilestoneInfo] = None
    can_checkin: bool


class CheckinInfo(BaseModel):
    consecutive_days: int
    reward_points: int
    daily_reward: DailyReward
    milestone_reward: Optional[DailyReward] = None
    is_milestone: bool


class CheckinResult(BaseModel):
    message: str
    checkin_info: CheckinInfo


class CheckinRecord(BaseModel):
    id: int
    checkin_date: str
    consecutive_days: int
    reward_points: int
    created_at: datetime

    class Config:
        from_attributes = True


class CheckinHistoryResponse(BaseModel):
    items: List[CheckinRecord]
    total: int
    page: int
    page_size: int
    total_pages: int


class CheckinStatistics(BaseModel):
    total_checkin_days: int
    total_points: int
    max_consecutive_days: int
    current_consecutive_days: int
    month_checkin_days: int


class CheckinCalendarDay(BaseModel):
    consecutive_days: int
    reward_points: int
    is_milestone: bool


class CheckinCalendarData(BaseModel):
    year: int
    month: int
    calendar: dict[int, CheckinCalendarDay]
    total_days: int