from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

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
        db: Session,
        reason: str = "系统冻结"
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
        db: Session,
        reason: str = "系统解冻", 
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
        db: Session,
        reason: str = "违约没收", 
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
    
    async def calculate_required_deposit(
        self, 
        auction_id: Optional[int], 
        product_value: Optional[Decimal], 
        db: Session
    ) -> Dict[str, Any]:
        """计算所需保证金金额"""
        
        # 基础保证金配置
        base_deposit = Decimal("100.00")  # 基础保证金100元
        percentage_rate = Decimal("0.1")  # 按商品价值10%计算
        max_deposit = Decimal("10000.00")  # 最高保证金10000元
        min_deposit = Decimal("50.00")    # 最低保证金50元
        
        if product_value and product_value > 0:
            # 按商品价值百分比计算
            calculated_deposit = product_value * percentage_rate
            # 确保在最大最小值范围内
            required_deposit = max(min_deposit, min(calculated_deposit, max_deposit))
        else:
            # 使用基础保证金
            required_deposit = base_deposit
        
        return {
            "required_amount": required_deposit,
            "calculation_method": "percentage" if product_value else "base",
            "product_value": product_value or Decimal("0.00"),
            "percentage_rate": float(percentage_rate * 100),  # 转换为百分比显示
            "min_deposit": min_deposit,
            "max_deposit": max_deposit
        }
    
    async def check_deposit_eligibility(
        self, 
        user_id: int, 
        auction_id: Optional[int], 
        required_amount: Decimal,
        db: Session
    ) -> Dict[str, Any]:
        """检查用户保证金缴纳资格"""
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("用户不存在")
        
        # 检查用户账户状态
        if getattr(user, 'status', 1) != 1:  # 假设1为正常状态
            return {
                "eligible": False,
                "reason": "账户状态异常，无法缴纳保证金"
            }
        
        # 检查是否已缴纳该拍卖的保证金
        if auction_id:
            existing_deposit = db.query(Deposit).filter(
                Deposit.user_id == user_id,
                Deposit.auction_id == auction_id,
                Deposit.status.in_(["active", "frozen"])
            ).first()
            
            if existing_deposit:
                return {
                    "eligible": False,
                    "reason": "您已为此拍卖缴纳保证金",
                    "existing_deposit_id": existing_deposit.id
                }
        
        # 检查用户余额（如果选择余额支付）
        balance_sufficient = user.balance >= required_amount
        
        # 检查用户保证金缴纳历史
        total_deposits = db.query(func.sum(Deposit.amount)).filter(
            Deposit.user_id == user_id,
            Deposit.status.in_(["active", "frozen"])
        ).scalar() or Decimal("0.00")
        
        # 保证金总额限制（比如不超过5万）
        deposit_limit = Decimal("50000.00")
        would_exceed_limit = (total_deposits + required_amount) > deposit_limit
        
        return {
            "eligible": not would_exceed_limit,
            "balance_sufficient": balance_sufficient,
            "current_balance": user.balance,
            "required_amount": required_amount,
            "total_deposits": total_deposits,
            "deposit_limit": deposit_limit,
            "would_exceed_limit": would_exceed_limit,
            "reason": "保证金总额将超过限制" if would_exceed_limit else None
        }
    
    async def auto_refund_expired_deposits(self, db: Session) -> List[Dict[str, Any]]:
        """自动退还过期保证金"""
        
        # 查找需要自动退还的保证金
        # 这里可以根据业务规则定义过期条件
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=30)  # 30天前的保证金
        
        expired_deposits = db.query(Deposit).filter(
            Deposit.status == "active",
            Deposit.auction_id.is_(None),  # 通用保证金
            Deposit.created_at < cutoff_date
        ).all()
        
        results = []
        
        for deposit in expired_deposits:
            try:
                # 执行退还
                user = db.query(User).filter(User.id == deposit.user_id).first()
                if user:
                    user.balance += deposit.amount
                    deposit.status = "refunded"
                    deposit.refunded_at = datetime.now()
                    
                    # 记录交易
                    wallet_transaction = WalletTransaction(
                        user_id=deposit.user_id,
                        type="recharge",
                        amount=deposit.amount,
                        balance_after=user.balance,
                        description=f"自动退还过期保证金 {deposit.amount}元",
                        status="completed"
                    )
                    db.add(wallet_transaction)
                    
                    # 记录日志
                    deposit_log = DepositLog(
                        deposit_id=deposit.id,
                        action="refund",
                        amount=deposit.amount,
                        reason="系统自动退还过期保证金"
                    )
                    db.add(deposit_log)
                    
                    results.append({
                        "deposit_id": deposit.id,
                        "user_id": deposit.user_id,
                        "amount": deposit.amount,
                        "success": True
                    })
                    
            except Exception as e:
                results.append({
                    "deposit_id": deposit.id,
                    "user_id": deposit.user_id,
                    "amount": deposit.amount,
                    "success": False,
                    "error": str(e)
                })
        
        if results:
            db.commit()
        
        return results
    
    async def get_deposit_statistics(self, db: Session) -> Dict[str, Any]:
        """获取保证金统计信息"""
        
        # 总体统计
        total_stats = db.query(
            func.count(Deposit.id).label('total_count'),
            func.sum(Deposit.amount).label('total_amount'),
            func.count(func.distinct(Deposit.user_id)).label('unique_users')
        ).first()
        
        # 按状态统计
        status_stats = db.query(
            Deposit.status,
            func.count(Deposit.id).label('count'),
            func.sum(Deposit.amount).label('amount')
        ).group_by(Deposit.status).all()
        
        # 按类型统计
        type_stats = db.query(
            Deposit.type,
            func.count(Deposit.id).label('count'),
            func.sum(Deposit.amount).label('amount')
        ).group_by(Deposit.type).all()
        
        # 最近30天统计
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_stats = db.query(
            func.count(Deposit.id).label('recent_count'),
            func.sum(Deposit.amount).label('recent_amount')
        ).filter(Deposit.created_at >= thirty_days_ago).first()
        
        return {
            "total": {
                "count": total_stats.total_count or 0,
                "amount": float(total_stats.total_amount or 0),
                "unique_users": total_stats.unique_users or 0
            },
            "by_status": [
                {
                    "status": stat.status,
                    "count": stat.count,
                    "amount": float(stat.amount or 0)
                }
                for stat in status_stats
            ],
            "by_type": [
                {
                    "type": stat.type,
                    "count": stat.count,
                    "amount": float(stat.amount or 0)
                }
                for stat in type_stats
            ],
            "recent_30_days": {
                "count": recent_stats.recent_count or 0,
                "amount": float(recent_stats.recent_amount or 0)
            }
        }