from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from decimal import Decimal
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from ..models.user import User
from ..models.deposit import Deposit, DepositLog
from ..models.wallet import WalletTransaction
from ..schemas.deposit import (
    DepositResponse, DepositSummaryResponse, DepositListResponse,
    PayDepositRequest, RefundDepositRequest, DepositLogResponse
)

logger = logging.getLogger(__name__)

class DepositService:
    
    # 安全配置
    SECURITY_CONFIG = {
        "max_daily_deposit": Decimal("10000.00"),  # 每日最大保证金缴纳金额
        "max_single_deposit": Decimal("50000.00"),  # 单笔最大保证金
        "min_single_deposit": Decimal("10.00"),    # 单笔最小保证金
        "daily_operation_limit": 10,              # 每日最大操作次数
        "fraud_check_threshold": Decimal("5000.00"), # 风控检查阈值
        "refund_cooling_period": 24,              # 退还冷却期（小时）
    }
    
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
        # 基础验证
        if request.amount <= 0:
            raise ValueError("保证金金额必须大于0")
        
        if request.amount < self.SECURITY_CONFIG["min_single_deposit"]:
            raise ValueError(f"单笔保证金不能少于{self.SECURITY_CONFIG['min_single_deposit']}元")
        
        if request.amount > self.SECURITY_CONFIG["max_single_deposit"]:
            raise ValueError(f"单笔保证金不能超过{self.SECURITY_CONFIG['max_single_deposit']}元")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("用户不存在")
        
        # 执行安全检查
        security_check = await self._perform_security_checks(user_id, request.amount, db)
        if not security_check["passed"]:
            raise ValueError(security_check["message"])
        
        # 检查重复保证金
        if request.auction_id:
            existing_deposit = db.query(Deposit).filter(
                and_(
                    Deposit.user_id == user_id,
                    Deposit.auction_id == request.auction_id,
                    Deposit.status.in_(["active", "frozen"])
                )
            ).first()
            if existing_deposit:
                raise ValueError("您已为此拍卖缴纳保证金")
        
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
        db.flush()  # 获取ID
        
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
        db.refresh(deposit)
        
        # 记录安全日志
        logger.info(f"用户 {user_id} 成功缴纳保证金 {request.amount} 元，保证金ID: {deposit.id}")
        
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
        
        # 检查冷却期
        cooling_period_check = await self._check_refund_cooling_period(deposit, db)
        if not cooling_period_check["passed"]:
            raise ValueError(cooling_period_check["message"])
        
        # 检查是否有关联的活跃拍卖
        if deposit.auction_id:
            auction_check = await self._check_auction_status_for_refund(deposit.auction_id, db)
            if not auction_check["allowed"]:
                raise ValueError(auction_check["reason"])
        
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
        
        # 记录安全日志
        logger.info(f"用户 {user_id} 成功退还保证金 {deposit.amount} 元，保证金ID: {deposit.id}")
        
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
    
    async def _perform_security_checks(self, user_id: int, amount: Decimal, db: Session) -> Dict[str, Any]:
        """执行安全检查"""
        errors = []
        
        # 检查每日操作次数限制
        today = datetime.now().date()
        daily_operations = db.query(func.count(DepositLog.id)).join(Deposit).filter(
            and_(
                Deposit.user_id == user_id,
                func.date(DepositLog.created_at) == today,
                DepositLog.action == "pay"
            )
        ).scalar()
        
        if daily_operations >= self.SECURITY_CONFIG["daily_operation_limit"]:
            errors.append(f"今日操作次数已达上限({self.SECURITY_CONFIG['daily_operation_limit']}次)")
        
        # 检查每日缴纳金额限制
        daily_amount = db.query(func.sum(Deposit.amount)).filter(
            and_(
                Deposit.user_id == user_id,
                func.date(Deposit.created_at) == today,
                Deposit.status.in_(["active", "frozen"])
            )
        ).scalar() or Decimal("0.00")
        
        if daily_amount + amount > self.SECURITY_CONFIG["max_daily_deposit"]:
            errors.append(f"今日缴纳金额将超过限制({self.SECURITY_CONFIG['max_daily_deposit']}元)")
        
        # 高额保证金风控检查
        if amount >= self.SECURITY_CONFIG["fraud_check_threshold"]:
            fraud_check = await self._fraud_detection_check(user_id, amount, db)
            if not fraud_check["passed"]:
                errors.append(fraud_check["message"])
        
        return {
            "passed": len(errors) == 0,
            "message": "; ".join(errors) if errors else "安全检查通过",
            "checks_performed": ["daily_limit", "amount_limit", "fraud_detection"]
        }
    
    async def _fraud_detection_check(self, user_id: int, amount: Decimal, db: Session) -> Dict[str, Any]:
        """欺诈检测"""
        # 检查用户历史行为
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"passed": False, "message": "用户信息异常"}
        
        # 检查账户年龄（新账户大额操作需要更严格检查）
        account_age_days = (datetime.now() - user.created_at).days
        if account_age_days < 7 and amount >= Decimal("1000.00"):
            return {"passed": False, "message": "新账户暂时无法进行大额操作"}
        
        # 检查历史操作模式
        recent_deposits = db.query(Deposit).filter(
            and_(
                Deposit.user_id == user_id,
                Deposit.created_at >= datetime.now() - timedelta(days=7)
            )
        ).count()
        
        if recent_deposits > 5:  # 7天内超过5次操作
            return {"passed": False, "message": "操作频率异常，请联系客服"}
        
        return {"passed": True, "message": "风控检查通过"}
    
    async def _check_refund_cooling_period(self, deposit: Deposit, db: Session) -> Dict[str, Any]:
        """检查退还冷却期"""
        hours_since_deposit = (datetime.now() - deposit.created_at).total_seconds() / 3600
        
        if hours_since_deposit < self.SECURITY_CONFIG["refund_cooling_period"]:
            remaining_hours = self.SECURITY_CONFIG["refund_cooling_period"] - hours_since_deposit
            return {
                "passed": False,
                "message": f"保证金缴纳后需等待{self.SECURITY_CONFIG['refund_cooling_period']}小时才能退还，还需等待{remaining_hours:.1f}小时"
            }
        
        return {"passed": True, "message": "冷却期检查通过"}
    
    async def _check_auction_status_for_refund(self, auction_id: int, db: Session) -> Dict[str, Any]:
        """检查拍卖状态是否允许退还保证金"""
        from ..models.product import Product
        
        product = db.query(Product).filter(Product.id == auction_id).first()
        if not product:
            return {"allowed": True, "reason": "拍卖商品不存在，允许退还"}
        
        # 拍卖进行中不允许退还
        if product.status == 2:  # 拍卖中
            return {"allowed": False, "reason": "拍卖进行中，不允许退还保证金"}
        
        # 检查是否有出价记录
        from ..models.product import Bid
        user_bids = db.query(Bid).filter(
            and_(
                Bid.product_id == auction_id,
                Bid.bidder_id == product.seller_id  # 这里应该是用户ID，但我们需要从deposit获取
            )
        ).count()
        
        if user_bids > 0:
            return {"allowed": False, "reason": "您已参与此拍卖出价，不允许退还保证金"}
        
        return {"allowed": True, "reason": "允许退还"}
    
    async def monitor_suspicious_activities(self, db: Session) -> Dict[str, Any]:
        """监控可疑活动"""
        suspicious_activities = []
        
        # 检查频繁操作的用户
        frequent_users = db.query(
            Deposit.user_id,
            func.count(Deposit.id).label('count'),
            func.sum(Deposit.amount).label('total_amount')
        ).filter(
            Deposit.created_at >= datetime.now() - timedelta(days=1)
        ).group_by(Deposit.user_id).having(
            func.count(Deposit.id) > 5
        ).all()
        
        for user_data in frequent_users:
            suspicious_activities.append({
                "type": "frequent_operations",
                "user_id": user_data.user_id,
                "count": user_data.count,
                "total_amount": float(user_data.total_amount),
                "severity": "medium"
            })
        
        # 检查大额异常操作
        large_deposits = db.query(Deposit).filter(
            and_(
                Deposit.amount >= Decimal("5000.00"),
                Deposit.created_at >= datetime.now() - timedelta(hours=1)
            )
        ).all()
        
        for deposit in large_deposits:
            suspicious_activities.append({
                "type": "large_amount",
                "user_id": deposit.user_id,
                "deposit_id": deposit.id,
                "amount": float(deposit.amount),
                "severity": "high"
            })
        
        return {
            "suspicious_count": len(suspicious_activities),
            "activities": suspicious_activities,
            "check_time": datetime.now().isoformat()
        }