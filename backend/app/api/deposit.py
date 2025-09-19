from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal

from ..core.database import get_db
from ..core.security import get_current_user, get_admin_user
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

@router.post("/calculate-required")
async def calculate_required_deposit(
    auction_id: Optional[int] = None,
    product_value: Optional[float] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """计算所需保证金金额"""
    try:
        deposit_service = DepositService()
        result = await deposit_service.calculate_required_deposit(
            auction_id=auction_id,
            product_value=Decimal(str(product_value)) if product_value else None,
            db=db
        )
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"计算保证金失败: {str(e)}")

@router.post("/check-eligibility")
async def check_deposit_eligibility(
    auction_id: Optional[int] = None,
    required_amount: float = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """检查保证金缴纳资格"""
    try:
        deposit_service = DepositService()
        result = await deposit_service.check_deposit_eligibility(
            user_id=current_user.id,
            auction_id=auction_id,
            required_amount=Decimal(str(required_amount)),
            db=db
        )
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检查资格失败: {str(e)}")

@router.post("/admin/auto-refund")
async def auto_refund_expired_deposits(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """自动退还过期保证金（管理员功能）"""
    try:
        deposit_service = DepositService()
        results = await deposit_service.auto_refund_expired_deposits(db)
        
        success_count = sum(1 for r in results if r.get("success"))
        
        return {
            "success": True,
            "message": f"处理完成，成功退还 {success_count} 笔保证金",
            "data": {
                "total_processed": len(results),
                "success_count": success_count,
                "details": results
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"自动退还失败: {str(e)}")

@router.get("/admin/statistics")
async def get_deposit_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """获取保证金统计信息（管理员功能）"""
    try:
        deposit_service = DepositService()
        stats = await deposit_service.get_deposit_statistics(db)
        
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")

@router.post("/admin/{deposit_id}/freeze")
async def freeze_deposit(
    deposit_id: int,
    reason: str = "管理员操作",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """冻结保证金（管理员功能）"""
    try:
        deposit_service = DepositService()
        success = await deposit_service.freeze_deposit(deposit_id, db, reason)
        
        if success:
            return {
                "success": True,
                "message": "保证金冻结成功"
            }
        else:
            raise HTTPException(status_code=400, detail="冻结失败，保证金状态异常")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"冻结保证金失败: {str(e)}")

@router.post("/admin/{deposit_id}/unfreeze")
async def unfreeze_deposit(
    deposit_id: int,
    reason: str = "管理员操作",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """解冻保证金（管理员功能）"""
    try:
        deposit_service = DepositService()
        success = await deposit_service.unfreeze_deposit(deposit_id, db, reason)
        
        if success:
            return {
                "success": True,
                "message": "保证金解冻成功"
            }
        else:
            raise HTTPException(status_code=400, detail="解冻失败，保证金状态异常")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解冻保证金失败: {str(e)}")

@router.post("/admin/{deposit_id}/forfeit")
async def forfeit_deposit(
    deposit_id: int,
    reason: str = "违约没收",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """没收保证金（管理员功能）"""
    try:
        deposit_service = DepositService()
        success = await deposit_service.forfeit_deposit(deposit_id, db, reason)
        
        if success:
            return {
                "success": True,
                "message": "保证金没收成功"
            }
        else:
            raise HTTPException(status_code=400, detail="没收失败，保证金状态异常")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"没收保证金失败: {str(e)}")