from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from decimal import Decimal
from typing import List, Dict, Any

from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..schemas.wallet import WalletResponse, RechargeRequest, RechargeResponse
from ..services.wallet_service import WalletService

router = APIRouter()

@router.get("/", response_model=WalletResponse)
async def get_wallet(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户钱包信息"""
    try:
        wallet_service = WalletService()
        wallet_info = await wallet_service.get_wallet_info(current_user.id, db)
        return wallet_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取钱包信息失败: {str(e)}")

@router.post("/recharge", response_model=RechargeResponse)
async def recharge_wallet(
    recharge_data: RechargeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """钱包充值"""
    try:
        wallet_service = WalletService()
        result = await wallet_service.recharge_wallet(
            user_id=current_user.id,
            amount=recharge_data.amount,
            payment_method=recharge_data.payment_method,
            db=db
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"充值失败: {str(e)}")

@router.get("/transactions")
async def get_transactions(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取钱包交易记录"""
    try:
        wallet_service = WalletService()
        transactions = await wallet_service.get_transactions(
            user_id=current_user.id,
            page=page,
            page_size=page_size,
            db=db
        )
        return transactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取交易记录失败: {str(e)}")

@router.post("/recharge/notify")
async def handle_recharge_notify(
    request: Request,
    db: Session = Depends(get_db)
):
    """处理钱包充值支付宝回调通知"""
    try:
        # 获取支付宝回调数据
        form_data = await request.form()
        notify_data = dict(form_data)
        
        # 从商户订单号中提取充值订单ID
        out_trade_no = notify_data.get("out_trade_no", "")
        trade_status = notify_data.get("trade_status", "")
        
        print(f"收到钱包充值回调: out_trade_no={out_trade_no}, trade_status={trade_status}")
        
        # 处理充值成功的情况
        if trade_status in ["TRADE_SUCCESS", "TRADE_FINISHED"]:
            wallet_service = WalletService()
            success = await wallet_service.complete_recharge(out_trade_no, db)
            
            if success:
                print(f"钱包充值完成: {out_trade_no}")
                return "success"
            else:
                print(f"钱包充值处理失败: {out_trade_no}")
                return "fail"
        
        return "success"  # 其他状态也返回success避免重复回调
        
    except Exception as e:
        print(f"处理钱包充值回调失败: {e}")
        return "fail"
