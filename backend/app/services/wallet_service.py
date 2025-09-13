from sqlalchemy.orm import Session
from decimal import Decimal
from typing import List, Dict, Any
import uuid
from datetime import datetime

from ..models.user import User
from ..models.wallet import WalletTransaction
from ..schemas.wallet import WalletResponse, RechargeResponse, TransactionResponse, TransactionListResponse
from ..services.alipay_service import AlipayService

class WalletService:
    def __init__(self):
        self.alipay_service = AlipayService()

    async def get_wallet_info(self, user_id: int, db: Session) -> WalletResponse:
        """获取用户钱包信息"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("用户不存在")
        
        # 计算总充值金额
        total_recharge = db.query(WalletTransaction).filter(
            WalletTransaction.user_id == user_id,
            WalletTransaction.type == "recharge",
            WalletTransaction.status == "completed"
        ).with_entities(WalletTransaction.amount).all()
        total_recharge_amount = sum(t[0] for t in total_recharge) if total_recharge else Decimal('0.00')
        
        # 计算总消费金额
        total_consumption = db.query(WalletTransaction).filter(
            WalletTransaction.user_id == user_id,
            WalletTransaction.type == "consumption",
            WalletTransaction.status == "completed"
        ).with_entities(WalletTransaction.amount).all()
        total_consumption_amount = sum(t[0] for t in total_consumption) if total_consumption else Decimal('0.00')
        
        return WalletResponse(
            balance=user.balance,
            frozen_amount=Decimal('0.00'),  # 暂时没有冻结金额功能
            total_recharge=total_recharge_amount,
            total_consumption=total_consumption_amount
        )

    async def recharge_wallet(
        self, 
        user_id: int, 
        amount: Decimal, 
        payment_method: str, 
        db: Session
    ) -> RechargeResponse:
        """钱包充值"""
        if amount <= 0:
            raise ValueError("充值金额必须大于0")
        
        if amount > Decimal('10000.00'):
            raise ValueError("单次充值金额不能超过10000元")
        
        # 创建充值订单
        order_id = f"RECHARGE_{uuid.uuid4().hex[:16].upper()}"
        
        # 创建交易记录
        transaction = WalletTransaction(
            user_id=user_id,
            type="recharge",
            amount=amount,
            balance_after=Decimal('0.00'),  # 充值成功后更新
            description=f"钱包充值 {amount}元",
            status="pending",
            order_id=order_id
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        # 根据支付方式生成支付信息
        if payment_method == "alipay":
            try:
                # 创建支付宝支付订单
                payment_result = await self.alipay_service.create_payment(
                    out_trade_no=order_id,
                    total_amount=float(amount),
                    subject=f"钱包充值 {amount}元",
                    body=f"宠物商店钱包充值"
                )
                
                return RechargeResponse(
                    order_id=order_id,
                    payment_url=payment_result.get('payment_url'),
                    order_string=payment_result.get('order_string'),
                    amount=amount,
                    status="pending"
                )
            except Exception as e:
                # 支付创建失败，更新交易状态
                transaction.status = "failed"
                transaction.description = f"充值失败: {str(e)}"
                db.commit()
                raise ValueError(f"创建支付订单失败: {str(e)}")
        else:
            raise ValueError(f"不支持的支付方式: {payment_method}")

    async def get_transactions(
        self, 
        user_id: int, 
        page: int, 
        page_size: int, 
        db: Session
    ) -> TransactionListResponse:
        """获取钱包交易记录"""
        query = db.query(WalletTransaction).filter(WalletTransaction.user_id == user_id)
        total = query.count()
        
        transactions = query.order_by(WalletTransaction.created_at.desc()).offset(
            (page - 1) * page_size
        ).limit(page_size).all()
        
        transaction_list = []
        for t in transactions:
            transaction_list.append(TransactionResponse(
                id=t.id,
                type=t.type,
                amount=t.amount,
                balance_after=t.balance_after,
                description=t.description,
                status=t.status,
                created_at=t.created_at
            ))
        
        return TransactionListResponse(
            items=transaction_list,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )

    async def complete_recharge(self, order_id: str, db: Session) -> bool:
        """完成充值（支付成功后调用）"""
        transaction = db.query(WalletTransaction).filter(
            WalletTransaction.order_id == order_id,
            WalletTransaction.status == "pending"
        ).first()
        
        if not transaction:
            return False
        
        # 更新用户余额
        user = db.query(User).filter(User.id == transaction.user_id).first()
        if not user:
            return False
        
        user.balance += transaction.amount
        transaction.balance_after = user.balance
        transaction.status = "completed"
        transaction.completed_at = datetime.utcnow()
        
        db.commit()
        return True

    async def consume_balance(self, user_id: int, amount: Decimal, description: str, db: Session) -> bool:
        """消费余额"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        if user.balance < amount:
            return False
        
        # 扣除余额
        user.balance -= amount
        
        # 创建消费记录
        transaction = WalletTransaction(
            user_id=user_id,
            type="consumption",
            amount=amount,
            balance_after=user.balance,
            description=description,
            status="completed"
        )
        db.add(transaction)
        db.commit()
        
        return True
