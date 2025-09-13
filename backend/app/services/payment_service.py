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