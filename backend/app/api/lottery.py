from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Optional

from ..core.database import get_db
from ..core.security import get_current_user, get_admin_user
from ..models.user import User
from ..services.lottery_service import LotteryService
from ..schemas.lottery import (
    LotteryDrawRequest, LotteryDrawResult, 
    LotteryHistoryResponse, LotteryConfigResponse
)

router = APIRouter(prefix="/lottery", tags=["抽奖"])

@router.get("/config", response_model=LotteryConfigResponse)
async def get_lottery_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取抽奖配置"""
    try:
        lottery_service = LotteryService()
        config = await lottery_service.get_lottery_config(db, current_user.id)
        
        return LotteryConfigResponse(**config)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取抽奖配置失败: {str(e)}")

@router.post("/draw", response_model=LotteryDrawResult)
async def draw_lottery(
    request: Request,
    draw_request: LotteryDrawRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """执行抽奖"""
    try:
        lottery_service = LotteryService()
        
        # 获取客户端信息
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent", "")
        
        result = await lottery_service.draw_lottery(
            db=db,
            user_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return LotteryDrawResult(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"抽奖失败: {str(e)}")

@router.get("/history", response_model=LotteryHistoryResponse)
async def get_lottery_history(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取抽奖历史"""
    try:
        lottery_service = LotteryService()
        result = await lottery_service.get_lottery_history(
            db=db,
            user_id=current_user.id,
            page=page,
            page_size=page_size
        )
        
        return LotteryHistoryResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取抽奖历史失败: {str(e)}")

@router.post("/claim/{record_id}")
async def claim_prize(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """领取奖品"""
    try:
        lottery_service = LotteryService()
        result = await lottery_service.claim_prize(
            db=db,
            user_id=current_user.id,
            record_id=record_id
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"领取奖品失败: {str(e)}")

# 管理员接口
@router.get("/admin/statistics")
async def get_lottery_statistics(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """获取抽奖统计（管理员）"""
    try:
        lottery_service = LotteryService()
        result = await lottery_service.get_lottery_statistics(db, days)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取抽奖统计失败: {str(e)}")

@router.post("/admin/init-prizes")
async def init_default_prizes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """初始化默认奖品（管理员）"""
    try:
        lottery_service = LotteryService()
        success = await lottery_service.init_default_prizes(db)
        
        if success:
            return {"success": True, "message": "默认奖品初始化成功"}
        else:
            return {"success": False, "message": "默认奖品初始化失败"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"初始化奖品失败: {str(e)}")
