from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from decimal import Decimal
from typing import List

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
