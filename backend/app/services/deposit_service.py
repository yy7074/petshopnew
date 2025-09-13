from sqlalchemy.orm import Session
from decimal import Decimal
from typing import List, Optional
from datetime import datetime

from ..models.user import User
from ..models.deposit import Deposit, DepositLog
from ..models.wallet import WalletTransaction
from ..schemas.deposit import (
    DepositResponse, DepositSummaryResponse, DepositListResponse,
    PayDepositRequest, RefundDepositRequest, DepositLogResponse
)

class DepositService:
    
    async def get_deposit_summary(self, user_id: int, db: Session) -> DepositSummaryResponse:
        """获取用户保证金汇总信息"""
        deposits = db.query(Deposit).filter(Deposit.user_id == user_id).all()
        
        total_deposit = Decimal('0.00')
        active_deposit = Decimal('0.00')
        frozen_deposit = Decimal('0.00')
        available_for_refund = Decimal('0.00')
        
        for deposit in deposits:
            total_deposit += deposit.amount
            
            if deposit.status == "active":
                active_deposit += deposit.amount
                available_for_refund += deposit.amount
            elif deposit.status == "frozen":
                frozen_deposit += deposit.amount
        
        return DepositSummaryResponse(
            total_deposit=total_deposit,
            active_deposit=active_deposit,
            frozen_deposit=frozen_deposit,
            available_for_refund=available_for_refund
        )
    
    async def get_user_deposits(
        self, 
        user_id: int, 
        page: int, 
        page_size: int, 
        db: Session
    ) -> DepositListResponse:
        """获取用户保证金列表"""
        query = db.query(Deposit).filter(Deposit.user_id == user_id)
        total = query.count()
        
        deposits = query.order_by(Deposit.created_at.desc()).offset(
            (page - 1) * page_size
        ).limit(page_size).all()
        
        deposit_list = []
        for deposit in deposits:
            deposit_list.append(DepositResponse(
                id=deposit.id,
                user_id=deposit.user_id,
                auction_id=deposit.auction_id,
                amount=deposit.amount,
                type=deposit.type,
                status=deposit.status,
                description=deposit.description,
                payment_method=deposit.payment_method,
                transaction_id=deposit.transaction_id,
                created_at=deposit.created_at,
                updated_at=deposit.updated_at,
                refunded_at=deposit.refunded_at
            ))
        
        return DepositListResponse(
            items=deposit_list,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )
    
    async def pay_deposit(
        self, 
        user_id: int, 
        request: PayDepositRequest, 
        db: Session
    ) -> DepositResponse:
        """缴纳保证金"""
        if request.amount <= 0:
            raise ValueError("保证金金额必须大于0")
        
        if request.amount > Decimal('50000.00'):
            raise ValueError("单笔保证金不能超过50000元")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("用户不存在")
        
        # 检查余额支付方式
        if request.payment_method == "balance":
            if user.balance < request.amount:
                raise ValueError("余额不足，请先充值")
            
            # 扣除余额
            user.balance -= request.amount
            
            # 创建钱包交易记录
            wallet_transaction = WalletTransaction(
                user_id=user_id,
                type="consumption",
                amount=request.amount,
                balance_after=user.balance,
                description=f"缴纳保证金 {request.amount}元",
                status="completed"
            )
            db.add(wallet_transaction)
        
        # 创建保证金记录
        deposit = Deposit(
            user_id=user_id,
            auction_id=request.auction_id,
            amount=request.amount,
            type=request.type,
            status="active",
            description=request.description or f"{request.type}保证金",
            payment_method=request.payment_method,
            transaction_id=f"DEPOSIT_{datetime.now().strftime('%Y%m%d%H%M%S')}{user_id}"
        )
        db.add(deposit)
        db.commit()
        db.refresh(deposit)
        
        # 记录操作日志
        deposit_log = DepositLog(
            deposit_id=deposit.id,
            action="pay",
            amount=request.amount,
            operator_id=user_id,
            reason="用户缴纳保证金"
        )
        db.add(deposit_log)
        db.commit()
        
        return DepositResponse(
            id=deposit.id,
            user_id=deposit.user_id,
            auction_id=deposit.auction_id,
            amount=deposit.amount,
            type=deposit.type,
            status=deposit.status,
            description=deposit.description,
            payment_method=deposit.payment_method,
            transaction_id=deposit.transaction_id,
            created_at=deposit.created_at,
            updated_at=deposit.updated_at,
            refunded_at=deposit.refunded_at
        )
    
    async def refund_deposit(
        self, 
        user_id: int, 
        request: RefundDepositRequest, 
        db: Session
    ) -> bool:
        """退还保证金"""
        deposit = db.query(Deposit).filter(
            Deposit.id == request.deposit_id,
            Deposit.user_id == user_id
        ).first()
        
        if not deposit:
            raise ValueError("保证金记录不存在")
        
        if deposit.status != "active":
            raise ValueError(f"保证金状态为{deposit.status}，无法退还")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("用户不存在")
        
        # 退还到用户余额
        user.balance += deposit.amount
        
        # 更新保证金状态
        deposit.status = "refunded"
        deposit.refunded_at = datetime.now()
        
        # 创建钱包交易记录
        wallet_transaction = WalletTransaction(
            user_id=user_id,
            type="recharge",
            amount=deposit.amount,
            balance_after=user.balance,
            description=f"退还保证金 {deposit.amount}元",
            status="completed"
        )
        db.add(wallet_transaction)
        
        # 记录操作日志
        deposit_log = DepositLog(
            deposit_id=deposit.id,
            action="refund",
            amount=deposit.amount,
            operator_id=user_id,
            reason=request.reason or "用户申请退还"
        )
        db.add(deposit_log)
        
        db.commit()
        return True
    
    async def freeze_deposit(
        self, 
        deposit_id: int, 
        reason: str = "系统冻结", 
        db: Session
    ) -> bool:
        """冻结保证金"""
        deposit = db.query(Deposit).filter(Deposit.id == deposit_id).first()
        if not deposit or deposit.status != "active":
            return False
        
        deposit.status = "frozen"
        
        # 记录操作日志
        deposit_log = DepositLog(
            deposit_id=deposit.id,
            action="freeze",
            amount=deposit.amount,
            reason=reason
        )
        db.add(deposit_log)
        db.commit()
        
        return True
    
    async def unfreeze_deposit(
        self, 
        deposit_id: int, 
        reason: str = "系统解冻", 
        db: Session
    ) -> bool:
        """解冻保证金"""
        deposit = db.query(Deposit).filter(Deposit.id == deposit_id).first()
        if not deposit or deposit.status != "frozen":
            return False
        
        deposit.status = "active"
        
        # 记录操作日志
        deposit_log = DepositLog(
            deposit_id=deposit.id,
            action="unfreeze",
            amount=deposit.amount,
            reason=reason
        )
        db.add(deposit_log)
        db.commit()
        
        return True
    
    async def forfeit_deposit(
        self, 
        deposit_id: int, 
        reason: str = "违约没收", 
        db: Session
    ) -> bool:
        """没收保证金"""
        deposit = db.query(Deposit).filter(Deposit.id == deposit_id).first()
        if not deposit or deposit.status not in ["active", "frozen"]:
            return False
        
        deposit.status = "forfeited"
        
        # 记录操作日志
        deposit_log = DepositLog(
            deposit_id=deposit.id,
            action="forfeit",
            amount=deposit.amount,
            reason=reason
        )
        db.add(deposit_log)
        db.commit()
        
        return True
    
    async def get_deposit_logs(
        self, 
        deposit_id: int, 
        db: Session
    ) -> List[DepositLogResponse]:
        """获取保证金操作日志"""
        logs = db.query(DepositLog).filter(
            DepositLog.deposit_id == deposit_id
        ).order_by(DepositLog.created_at.desc()).all()
        
        log_list = []
        for log in logs:
            log_list.append(DepositLogResponse(
                id=log.id,
                deposit_id=log.deposit_id,
                action=log.action,
                amount=log.amount,
                operator_id=log.operator_id,
                reason=log.reason,
                created_at=log.created_at
            ))
        
        return log_list