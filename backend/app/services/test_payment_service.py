"""
测试支付服务
用于开发环境测试支付功能
"""
from sqlalchemy.orm import Session
from typing import Dict, Any
import time
import uuid

from ..models.order import Order, Payment

class TestPaymentService:
    def __init__(self):
        pass

    async def create_payment(
        self,
        db: Session,
        order_id: int,
        user_id: int,
        return_url: str = None,
        notify_url: str = None
    ) -> Dict[str, Any]:
        """创建测试支付订单"""
        
        # 获取订单信息
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise ValueError("订单不存在")
            
        if order.buyer_id != user_id:
            raise ValueError("无权限支付此订单")

        # 生成商户订单号
        out_trade_no = f"TEST_{order_id}_{int(time.time())}"
        
        # 创建支付记录
        payment = Payment(
            order_id=order_id,
            user_id=user_id,
            payment_method=1,  # 1:支付宝
            amount=order.total_amount,
            transaction_id=out_trade_no,
            payment_type="payment",
            status="pending"
        )
        
        db.add(payment)
        db.commit()
        db.refresh(payment)
        
        # 返回模拟的支付参数
        return {
            "payment_id": payment.id,
            "order_string": f"test_order_string_{payment.id}",  # 模拟的支付字符串
            "out_trade_no": out_trade_no,
            "total_amount": str(order.total_amount),
            "subject": f"测试订单-{order.order_no}"
        }

    async def verify_notify(self, notify_data: Dict[str, Any]) -> bool:
        """验证测试支付回调通知"""
        return True  # 测试环境总是返回True

    async def handle_notify(
        self,
        db: Session,
        payment_id: int,
        notify_data: Dict[str, Any]
    ) -> bool:
        """处理测试支付回调通知"""
        try:
            payment = db.query(Payment).filter(Payment.id == payment_id).first()
            if not payment:
                return False
                
            # 模拟支付成功
            payment.status = "paid"
            payment.updated_at = time.time()
            
            # 更新订单状态
            order = db.query(Order).filter(Order.id == payment.order_id).first()
            if order:
                order.payment_status = 2  # 已支付
                order.order_status = 2  # 待发货
                order.paid_at = time.time()
            
            db.commit()
            return True
            
        except Exception as e:
            print(f"处理测试支付通知失败: {e}")
            return False

    async def query_payment(self, out_trade_no: str) -> Dict[str, Any]:
        """查询测试支付状态"""
        return {
            "trade_status": "TRADE_SUCCESS",
            "out_trade_no": out_trade_no,
            "total_amount": "0.01"
        }

    async def close_payment(self, out_trade_no: str) -> bool:
        """关闭测试支付订单"""
        return True

    async def refund(
        self,
        db: Session,
        payment_id: int,
        refund_amount: float = None,
        refund_reason: str = "用户申请退款"
    ) -> Dict[str, Any]:
        """申请测试退款"""
        try:
            payment = db.query(Payment).filter(Payment.id == payment_id).first()
            if not payment:
                raise ValueError("支付记录不存在")
                
            if payment.status != "paid":
                raise ValueError("订单未支付，无法退款")
                
            # 退款金额默认为支付金额
            if refund_amount is None:
                refund_amount = float(payment.amount)
                
            # 生成退款单号
            out_refund_no = f"REFUND_{payment_id}_{int(time.time())}"
            
            # 创建退款记录
            refund_payment = Payment(
                order_id=payment.order_id,
                user_id=payment.user_id,
                payment_method=payment.payment_method,
                amount=-refund_amount,  # 负数表示退款
                transaction_id=out_refund_no,
                payment_type="refund",
                status="refunded"
            )
            
            db.add(refund_payment)
            db.commit()
            
            return {
                "success": True,
                "refund_id": refund_payment.id,
                "out_refund_no": out_refund_no,
                "refund_amount": refund_amount
            }
                
        except Exception as e:
            print(f"测试退款失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
