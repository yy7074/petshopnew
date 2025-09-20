from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.checkin_service import CheckinService
from app.schemas.checkin import (
    CheckinStatus, CheckinResult, CheckinHistoryResponse, 
    CheckinStatistics, CheckinCalendarData
)

router = APIRouter()


@router.get("/status", response_model=CheckinStatus)
async def get_checkin_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户签到状态"""
    service = CheckinService(db)
    return service.get_checkin_status(current_user.id)


@router.post("/daily", response_model=CheckinResult)
async def daily_checkin(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """执行每日签到"""
    service = CheckinService(db)
    try:
        return service.daily_checkin(current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/history", response_model=CheckinHistoryResponse)
async def get_checkin_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取签到历史"""
    service = CheckinService(db)
    return service.get_checkin_history(current_user.id, page, page_size)


@router.get("/statistics", response_model=CheckinStatistics)
async def get_checkin_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取签到统计"""
    service = CheckinService(db)
    return service.get_checkin_statistics(current_user.id)


@router.get("/calendar", response_model=CheckinCalendarData)
async def get_checkin_calendar(
    year: int = Query(..., ge=2020, le=2030),
    month: int = Query(..., ge=1, le=12),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取签到日历"""
    service = CheckinService(db)
    return service.get_checkin_calendar(current_user.id, year, month)