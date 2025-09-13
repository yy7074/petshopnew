from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..schemas.deposit import (
    DepositSummaryResponse, DepositListResponse, DepositResponse,
    PayDepositRequest, RefundDepositRequest, DepositLogResponse
)
from ..services.deposit_service import DepositService

router = APIRouter()

@router.get("/summary", response_model=DepositSummaryResponse)
async def get_deposit_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户保证金汇总信息"""
    try:
        deposit_service = DepositService()
        summary = await deposit_service.get_deposit_summary(current_user.id, db)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取保证金信息失败: {str(e)}")

@router.get("/", response_model=DepositListResponse)
async def get_user_deposits(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户保证金列表"""
    try:
        deposit_service = DepositService()
        deposits = await deposit_service.get_user_deposits(
            user_id=current_user.id,
            page=page,
            page_size=page_size,
            db=db
        )
        return deposits
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取保证金列表失败: {str(e)}")

@router.post("/pay", response_model=DepositResponse)
async def pay_deposit(
    request: PayDepositRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """缴纳保证金"""
    try:
        deposit_service = DepositService()
        deposit = await deposit_service.pay_deposit(
            user_id=current_user.id,
            request=request,
            db=db
        )
        return deposit
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/refund")
async def refund_deposit(
    request: RefundDepositRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """申请退还保证金"""
    try:
        deposit_service = DepositService()
        success = await deposit_service.refund_deposit(
            user_id=current_user.id,
            request=request,
            db=db
        )
        
        if success:
            return {"message": "保证金退还成功", "success": True}
        else:
            raise HTTPException(status_code=400, detail="保证金退还失败")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{deposit_id}/logs", response_model=List[DepositLogResponse])
async def get_deposit_logs(
    deposit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取保证金操作日志"""
    try:
        # 验证保证金是否属于当前用户
        from ..models.deposit import Deposit
        deposit = db.query(Deposit).filter(
            Deposit.id == deposit_id,
            Deposit.user_id == current_user.id
        ).first()
        
        if not deposit:
            raise HTTPException(status_code=404, detail="保证金记录不存在")
        
        deposit_service = DepositService()
        logs = await deposit_service.get_deposit_logs(deposit_id, db)
        return logs
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取操作日志失败: {str(e)}")