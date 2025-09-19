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