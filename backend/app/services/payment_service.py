from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime
from decimal import Decimal
import uuid

from ..models.order import Payment, Order
from ..models.user import User
from ..schemas.order import PaymentCreate, PaymentResponse
from ..core.config import settings

class PaymentService:

    async def create_payment(
        self,
        db: Session,
        payment_data: PaymentCreate,
        user_id: int
    ) -> PaymentResponse:
        """创建支付记录"""
        # 验证订单
        order = db.query(Order).filter(Order.id == payment_data.order_id).first()
        if not order:
            raise ValueError("订单不存在")

        if order.buyer_id != user_id:
            raise ValueError("无权限支付此订单")

        if order.payment_status != 1:  # 1:待支付
            raise ValueError("订单状态不允许支付")

        # 生成交易号
        transaction_id = f"PAY{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4().int)[:6]}"

        # 创建支付记录
        payment = Payment(
            order_id=payment_data.order_id,
            user_id=user_id,
            payment_method=payment_data.payment_method,
            amount=payment_data.amount,
            transaction_id=transaction_id,
            payment_type="payment",
            status="pending"
        )

        db.add(payment)
        db.commit()
        db.refresh(payment)

        return self._to_payment_response(payment)

    async def get_payment_detail(
        self,
        db: Session,
        payment_id: int,
        user_id: int
    ) -> Optional[PaymentResponse]:
        """获取支付详情"""
        payment = db.query(Payment).filter(
            Payment.id == payment_id,
            Payment.user_id == user_id
        ).first()

        if not payment:
            return None

        return self._to_payment_response(payment)

    async def handle_payment_notify(
        self,
        db: Session,
        payment_id: int,
        notify_data: Dict[str, Any]
    ) -> bool:
        """处理支付回调通知"""
        try:
            payment = db.query(Payment).filter(Payment.id == payment_id).first()
            if not payment:
                return False

            # 验证支付状态
            if notify_data.get("status") == "success":
                payment.status = "paid"
                payment.updated_at = datetime.now()

                # 更新订单状态
                order = db.query(Order).filter(Order.id == payment.order_id).first()
                if order:
                    order.payment_status = 2  # 已支付
                    order.paid_at = datetime.now()

                db.commit()

                # 这里可以触发支付成功后续处理
                # await self.process_payment_success(db, payment_id)

                return True
            elif notify_data.get("status") == "failed":
                payment.status = "failed"
                payment.updated_at = datetime.now()
                db.commit()
                return True

            return False

        except Exception as e:
            print(f"处理支付通知失败: {e}")
            return False

    async def process_payment_success(
        self,
        db: Session,
        payment_id: int
    ):
        """处理支付成功后续流程"""
        try:
            payment = db.query(Payment).filter(Payment.id == payment_id).first()
            if not payment or payment.status != "paid":
                return

            # 更新订单状态
            order = db.query(Order).filter(Order.id == payment.order_id).first()
            if order:
                order.status = "paid"  # 从字符串改为数字状态码
                order.paid_at = datetime.now()

                # 这里可以添加其他支付成功后的逻辑：
                # - 发送通知
                # - 更新商品状态
                # - 处理分成等

            db.commit()

        except Exception as e:
            print(f"处理支付成功后续流程失败: {e}")

    async def create_refund(
        self,
        db: Session,
        order_id: int,
        amount: Decimal,
        reason: str,
        user_id: int
    ) -> Payment:
        """创建退款记录"""
        # 验证订单
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise ValueError("订单不存在")

        if order.buyer_id != user_id:
            raise ValueError("无权限申请退款")

        # 生成退款交易号
        refund_transaction_id = f"REFUND{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4().int)[:6]}"

        # 创建退款记录
        refund = Payment(
            order_id=order_id,
            user_id=user_id,
            payment_method=order.payment_method,
            amount=-amount,  # 负数表示退款
            transaction_id=refund_transaction_id,
            payment_type="refund",
            status="processing"
        )

        db.add(refund)
        db.commit()
        db.refresh(refund)

        return refund

    async def process_refund(
        self,
        db: Session,
        refund_id: int,
        success: bool = True
    ):
        """处理退款结果"""
        try:
            refund = db.query(Payment).filter(Payment.id == refund_id).first()
            if not refund or refund.payment_type != "refund":
                return

            if success:
                refund.status = "refunded"
                # 退款成功，返还用户余额
                user = db.query(User).filter(User.id == refund.user_id).first()
                if user:
                    user.balance += abs(refund.amount)
            else:
                refund.status = "failed"

            refund.updated_at = datetime.now()
            db.commit()

        except Exception as e:
            print(f"处理退款失败: {e}")

    async def get_user_payments(
        self,
        db: Session,
        user_id: int,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None
    ):
        """获取用户支付记录"""
        query = db.query(Payment).filter(Payment.user_id == user_id)

        if status:
            query = query.filter(Payment.status == status)

        query = query.order_by(Payment.created_at.desc())

        total = query.count()
        offset = (page - 1) * page_size
        payments = query.offset(offset).limit(page_size).all()

        return {
            "items": [self._to_payment_response(payment) for payment in payments],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }

    def _to_payment_response(self, payment: Payment) -> PaymentResponse:
        """转换为响应格式"""
        return PaymentResponse(
            id=payment.id,
            order_id=payment.order_id,
            user_id=payment.user_id,
            payment_method=payment.payment_method,
            amount=payment.amount,
            status=payment.status,
            transaction_id=payment.transaction_id,
            created_at=payment.created_at,
            updated_at=payment.updated_at
        )
    
    async def get_payment_statistics(self, db: Session) -> Dict[str, Any]:
        """获取支付统计数据"""
        from sqlalchemy import func
        from datetime import timedelta
        
        # 总体统计
        total_stats = db.query(
            func.count(Payment.id).label('total_payments'),
            func.sum(Payment.amount).label('total_amount'),
            func.count(func.distinct(Payment.user_id)).label('unique_users')
        ).filter(Payment.payment_type == "payment").first()
        
        # 按状态统计
        status_stats = db.query(
            Payment.status,
            func.count(Payment.id).label('count'),
            func.sum(Payment.amount).label('amount')
        ).filter(Payment.payment_type == "payment").group_by(Payment.status).all()
        
        # 按支付方式统计
        method_stats = db.query(
            Payment.payment_method,
            func.count(Payment.id).label('count'),
            func.sum(Payment.amount).label('amount')
        ).filter(Payment.payment_type == "payment").group_by(Payment.payment_method).all()
        
        # 最近30天统计
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_stats = db.query(
            func.count(Payment.id).label('recent_count'),
            func.sum(Payment.amount).label('recent_amount')
        ).filter(
            Payment.payment_type == "payment",
            Payment.created_at >= thirty_days_ago
        ).first()
        
        # 退款统计
        refund_stats = db.query(
            func.count(Payment.id).label('refund_count'),
            func.sum(func.abs(Payment.amount)).label('refund_amount')
        ).filter(Payment.payment_type == "refund").first()
        
        return {
            "total": {
                "payments": total_stats.total_payments or 0,
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
            "by_method": [
                {
                    "method": stat.payment_method,
                    "count": stat.count,
                    "amount": float(stat.amount or 0)
                }
                for stat in method_stats
            ],
            "recent_30_days": {
                "count": recent_stats.recent_count or 0,
                "amount": float(recent_stats.recent_amount or 0)
            },
            "refunds": {
                "count": refund_stats.refund_count or 0,
                "amount": float(refund_stats.refund_amount or 0)
            }
        }
    
    async def process_balance_payment(
        self,
        db: Session,
        order_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """处理余额支付"""
        
        # 获取订单信息
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise ValueError("订单不存在")
        
        if order.buyer_id != user_id:
            raise ValueError("无权限支付此订单")
        
        if order.payment_status != 1:  # 待支付
            raise ValueError("订单状态不允许支付")
        
        # 获取用户信息
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("用户不存在")
        
        # 检查余额
        if user.balance < order.total_amount:
            raise ValueError("余额不足，请先充值")
        
        # 扣除余额
        user.balance -= order.total_amount
        
        # 创建支付记录
        transaction_id = f"BAL{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4().int)[:6]}"
        payment = Payment(
            order_id=order_id,
            user_id=user_id,
            payment_method="balance",
            amount=order.total_amount,
            transaction_id=transaction_id,
            payment_type="payment",
            status="paid"
        )
        
        # 更新订单状态
        order.payment_status = 2  # 已支付
        order.order_status = 2   # 待发货
        order.paid_at = datetime.now()
        
        # 创建钱包交易记录
        from ..models.wallet import WalletTransaction
        wallet_transaction = WalletTransaction(
            user_id=user_id,
            type="consumption",
            amount=order.total_amount,
            balance_after=user.balance,
            description=f"支付订单 {order.order_no}",
            status="completed"
        )
        
        db.add(payment)
        db.add(wallet_transaction)
        db.commit()
        db.refresh(payment)
        
        return {
            "payment_id": payment.id,
            "transaction_id": transaction_id,
            "amount": float(order.total_amount),
            "balance_after": float(user.balance),
            "message": "余额支付成功"
        }
    
    async def validate_payment_amount(
        self,
        db: Session,
        order_id: int,
        amount: Decimal
    ) -> Dict[str, Any]:
        """验证支付金额"""
        
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise ValueError("订单不存在")
        
        is_valid = abs(amount - order.total_amount) < Decimal("0.01")  # 允许1分钱误差
        
        return {
            "is_valid": is_valid,
            "order_amount": float(order.total_amount),
            "payment_amount": float(amount),
            "difference": float(abs(amount - order.total_amount)),
            "message": "金额验证通过" if is_valid else "支付金额与订单金额不符"
        }
    
    async def get_payment_methods(self) -> Dict[str, Any]:
        """获取支持的支付方式"""
        
        methods = [
            {
                "code": "balance",
                "name": "余额支付",
                "description": "使用账户余额支付",
                "icon": "wallet",
                "enabled": True,
                "fee_rate": 0.0
            },
            {
                "code": "alipay",
                "name": "支付宝",
                "description": "支付宝快捷支付",
                "icon": "alipay",
                "enabled": True,
                "fee_rate": 0.006  # 0.6%手续费
            },
            {
                "code": "wechat",
                "name": "微信支付",
                "description": "微信快捷支付",
                "icon": "wechat",
                "enabled": False,  # 暂未开通
                "fee_rate": 0.006
            }
        ]
        
        return {
            "methods": methods,
            "default_method": "balance"
        }
    
    async def calculate_payment_fee(
        self,
        amount: Decimal,
        payment_method: str
    ) -> Dict[str, Any]:
        """计算支付手续费"""
        
        fee_rates = {
            "balance": Decimal("0.00"),
            "alipay": Decimal("0.006"),
            "wechat": Decimal("0.006")
        }
        
        fee_rate = fee_rates.get(payment_method, Decimal("0.00"))
        fee_amount = amount * fee_rate
        total_amount = amount + fee_amount
        
        return {
            "original_amount": float(amount),
            "fee_rate": float(fee_rate),
            "fee_amount": float(fee_amount),
            "total_amount": float(total_amount),
            "payment_method": payment_method
        }
    
    async def generate_payment_report(
        self,
        db: Session,
        start_date: datetime,
        end_date: datetime,
        group_by: str = "day"
    ) -> Dict[str, Any]:
        """生成支付报表"""
        from sqlalchemy import func, extract, case
        
        # 构建时间分组函数
        if group_by == "day":
            time_group = func.date(Payment.created_at)
        elif group_by == "week":
            time_group = func.date_trunc('week', Payment.created_at)
        elif group_by == "month":
            time_group = func.date_trunc('month', Payment.created_at)
        else:
            time_group = func.date(Payment.created_at)
        
        # 支付数据统计
        payment_stats = db.query(
            time_group.label('time_period'),
            func.count(Payment.id).label('total_payments'),
            func.sum(case([(Payment.status == 'paid', Payment.amount)], else_=0)).label('paid_amount'),
            func.sum(case([(Payment.status == 'pending', Payment.amount)], else_=0)).label('pending_amount'),
            func.sum(case([(Payment.status == 'failed', Payment.amount)], else_=0)).label('failed_amount'),
            func.count(case([(Payment.status == 'paid', 1)])).label('paid_count'),
            func.count(case([(Payment.status == 'pending', 1)])).label('pending_count'),
            func.count(case([(Payment.status == 'failed', 1)])).label('failed_count')
        ).filter(
            Payment.payment_type == "payment",
            Payment.created_at >= start_date,
            Payment.created_at <= end_date
        ).group_by(time_group).order_by(time_group).all()
        
        # 退款数据统计
        refund_stats = db.query(
            time_group.label('time_period'),
            func.count(Payment.id).label('refund_count'),
            func.sum(func.abs(Payment.amount)).label('refund_amount')
        ).filter(
            Payment.payment_type == "refund",
            Payment.created_at >= start_date,
            Payment.created_at <= end_date
        ).group_by(time_group).order_by(time_group).all()
        
        # 转换为字典以便合并
        refund_dict = {str(stat.time_period): stat for stat in refund_stats}
        
        # 合并数据
        report_data = []
        for payment_stat in payment_stats:
            period_str = str(payment_stat.time_period)
            refund_stat = refund_dict.get(period_str)
            
            report_data.append({
                "time_period": period_str,
                "payments": {
                    "total_count": payment_stat.total_payments,
                    "paid_count": payment_stat.paid_count,
                    "pending_count": payment_stat.pending_count,
                    "failed_count": payment_stat.failed_count,
                    "paid_amount": float(payment_stat.paid_amount or 0),
                    "pending_amount": float(payment_stat.pending_amount or 0),
                    "failed_amount": float(payment_stat.failed_amount or 0),
                    "success_rate": round(
                        (payment_stat.paid_count / payment_stat.total_payments * 100) 
                        if payment_stat.total_payments > 0 else 0, 2
                    )
                },
                "refunds": {
                    "count": refund_stat.refund_count if refund_stat else 0,
                    "amount": float(refund_stat.refund_amount or 0) if refund_stat else 0
                }
            })
        
        # 计算汇总数据
        total_paid_amount = sum(item["payments"]["paid_amount"] for item in report_data)
        total_refund_amount = sum(item["refunds"]["amount"] for item in report_data)
        total_payments = sum(item["payments"]["total_count"] for item in report_data)
        total_paid_count = sum(item["payments"]["paid_count"] for item in report_data)
        
        return {
            "summary": {
                "total_payments": total_payments,
                "total_paid_count": total_paid_count,
                "total_paid_amount": total_paid_amount,
                "total_refund_amount": total_refund_amount,
                "overall_success_rate": round(
                    (total_paid_count / total_payments * 100) if total_payments > 0 else 0, 2
                ),
                "net_amount": total_paid_amount - total_refund_amount
            },
            "data": report_data,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "group_by": group_by
            }
        }
    
    async def detect_payment_anomalies(self, db: Session) -> Dict[str, Any]:
        """检测支付异常"""
        from sqlalchemy import func, and_
        from datetime import timedelta
        
        anomalies = []
        
        # 检测高失败率的支付方式
        failure_rate_stats = db.query(
            Payment.payment_method,
            func.count(Payment.id).label('total'),
            func.count(case([(Payment.status == 'failed', 1)])).label('failed'),
            (func.count(case([(Payment.status == 'failed', 1)])) * 100.0 / func.count(Payment.id)).label('failure_rate')
        ).filter(
            Payment.payment_type == "payment",
            Payment.created_at >= datetime.now() - timedelta(days=7)
        ).group_by(Payment.payment_method).having(
            func.count(Payment.id) > 10  # 至少10笔交易
        ).all()
        
        for stat in failure_rate_stats:
            if stat.failure_rate > 20:  # 失败率超过20%
                anomalies.append({
                    "type": "high_failure_rate",
                    "payment_method": stat.payment_method,
                    "failure_rate": round(stat.failure_rate, 2),
                    "total_count": stat.total,
                    "failed_count": stat.failed,
                    "severity": "high" if stat.failure_rate > 50 else "medium"
                })
        
        # 检测异常大额支付
        large_payments = db.query(Payment).filter(
            and_(
                Payment.payment_type == "payment",
                Payment.amount >= Decimal("10000.00"),
                Payment.created_at >= datetime.now() - timedelta(hours=24)
            )
        ).all()
        
        for payment in large_payments:
            anomalies.append({
                "type": "large_amount",
                "payment_id": payment.id,
                "user_id": payment.user_id,
                "amount": float(payment.amount),
                "payment_method": payment.payment_method,
                "created_at": payment.created_at.isoformat(),
                "severity": "high" if payment.amount >= Decimal("50000.00") else "medium"
            })
        
        # 检测频繁退款用户
        frequent_refund_users = db.query(
            Payment.user_id,
            func.count(Payment.id).label('refund_count'),
            func.sum(func.abs(Payment.amount)).label('refund_amount')
        ).filter(
            and_(
                Payment.payment_type == "refund",
                Payment.created_at >= datetime.now() - timedelta(days=30)
            )
        ).group_by(Payment.user_id).having(
            func.count(Payment.id) > 5  # 30天内超过5次退款
        ).all()
        
        for user_stat in frequent_refund_users:
            anomalies.append({
                "type": "frequent_refunds",
                "user_id": user_stat.user_id,
                "refund_count": user_stat.refund_count,
                "refund_amount": float(user_stat.refund_amount),
                "severity": "medium"
            })
        
        return {
            "anomaly_count": len(anomalies),
            "anomalies": anomalies,
            "check_time": datetime.now().isoformat()
        }
    
    async def get_revenue_analytics(self, db: Session, days: int = 30) -> Dict[str, Any]:
        """获取收入分析"""
        from sqlalchemy import func
        
        start_date = datetime.now() - timedelta(days=days)
        
        # 收入趋势
        daily_revenue = db.query(
            func.date(Payment.created_at).label('date'),
            func.sum(Payment.amount).label('revenue'),
            func.count(Payment.id).label('transaction_count')
        ).filter(
            and_(
                Payment.payment_type == "payment",
                Payment.status == "paid",
                Payment.created_at >= start_date
            )
        ).group_by(func.date(Payment.created_at)).order_by(func.date(Payment.created_at)).all()
        
        # 按支付方式分析
        method_revenue = db.query(
            Payment.payment_method,
            func.sum(Payment.amount).label('revenue'),
            func.count(Payment.id).label('transaction_count'),
            func.avg(Payment.amount).label('avg_amount')
        ).filter(
            and_(
                Payment.payment_type == "payment",
                Payment.status == "paid",
                Payment.created_at >= start_date
            )
        ).group_by(Payment.payment_method).all()
        
        # 用户支付行为分析
        user_behavior = db.query(
            func.count(func.distinct(Payment.user_id)).label('active_users'),
            func.avg(Payment.amount).label('avg_payment'),
            func.percentile_cont(0.5).within_group(Payment.amount).label('median_payment'),
            func.max(Payment.amount).label('max_payment'),
            func.min(Payment.amount).label('min_payment')
        ).filter(
            and_(
                Payment.payment_type == "payment",
                Payment.status == "paid",
                Payment.created_at >= start_date
            )
        ).first()
        
        # 计算增长率
        previous_period_revenue = db.query(
            func.sum(Payment.amount)
        ).filter(
            and_(
                Payment.payment_type == "payment",
                Payment.status == "paid",
                Payment.created_at >= start_date - timedelta(days=days),
                Payment.created_at < start_date
            )
        ).scalar() or Decimal("0.00")
        
        current_period_revenue = sum(day.revenue for day in daily_revenue)
        
        growth_rate = 0
        if previous_period_revenue > 0:
            growth_rate = ((current_period_revenue - previous_period_revenue) / previous_period_revenue) * 100
        
        return {
            "period": {
                "days": days,
                "start_date": start_date.isoformat(),
                "end_date": datetime.now().isoformat()
            },
            "summary": {
                "total_revenue": float(current_period_revenue),
                "previous_period_revenue": float(previous_period_revenue),
                "growth_rate": round(growth_rate, 2),
                "active_users": user_behavior.active_users or 0,
                "avg_payment": float(user_behavior.avg_payment or 0),
                "median_payment": float(user_behavior.median_payment or 0),
                "max_payment": float(user_behavior.max_payment or 0),
                "min_payment": float(user_behavior.min_payment or 0)
            },
            "daily_trend": [
                {
                    "date": str(day.date),
                    "revenue": float(day.revenue),
                    "transaction_count": day.transaction_count
                }
                for day in daily_revenue
            ],
            "by_payment_method": [
                {
                    "method": method.payment_method,
                    "revenue": float(method.revenue),
                    "transaction_count": method.transaction_count,
                    "avg_amount": float(method.avg_amount)
                }
                for method in method_revenue
            ]
        }