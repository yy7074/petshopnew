from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.request.AlipayTradeAppPayRequest import AlipayTradeAppPayRequest
from alipay.aop.api.request.AlipayTradePagePayRequest import AlipayTradePagePayRequest
from alipay.aop.api.request.AlipayTradeQueryRequest import AlipayTradeQueryRequest
from alipay.aop.api.request.AlipayTradeCloseRequest import AlipayTradeCloseRequest
from alipay.aop.api.request.AlipayTradeRefundRequest import AlipayTradeRefundRequest
from alipay.aop.api.util.SignatureUtils import verify_with_rsa
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from decimal import Decimal
import uuid
import json
from datetime import datetime
from urllib.parse import parse_qs, unquote

from ..core.config import settings
from ..models.order import Order, Payment
from ..schemas.order import PaymentCreate

class AlipayService:
    def __init__(self):
        # 创建支付宝客户端配置
        alipay_config = AlipayClientConfig()
        alipay_config.server_url = "https://openapi.alipay.com/gateway.do"  # 正式环境
        if settings.DEBUG:
            alipay_config.server_url = "https://openapi.alipaydev.com/gateway.do"  # 沙箱环境
        
        alipay_config.app_id = settings.ALIPAY_APP_ID
        alipay_config.app_private_key = settings.ALIPAY_PRIVATE_KEY
        alipay_config.alipay_public_key = settings.ALIPAY_PUBLIC_KEY
        alipay_config.sign_type = "RSA2"
        
        self.alipay_client = DefaultAlipayClient(alipay_config)

    async def create_payment(
        self,
        db: Session,
        order_id: int,
        user_id: int,
        return_url: str = None,
        notify_url: str = None
    ) -> Dict[str, Any]:
        """创建支付宝支付订单"""
        
        # 获取订单信息
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise ValueError("订单不存在")
            
        if order.buyer_id != user_id:
            raise ValueError("无权限支付此订单")
            
        if order.payment_status != 1:  # 1:待支付
            raise ValueError("订单状态不允许支付")

        # 生成商户订单号
        out_trade_no = f"ORDER_{order_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 订单信息
        subject = f"宠物拍卖订单-{order.order_no}"
        body = f"订单号: {order.order_no}"
        total_amount = str(order.total_amount)
        
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
        
        # 构建App支付请求
        request = AlipayTradeAppPayRequest()
        biz_content = {
            "out_trade_no": out_trade_no,
            "total_amount": total_amount,
            "subject": subject,
            "body": body,
            "timeout_express": "30m"
        }
        request.biz_content = json.dumps(biz_content)
        request.notify_url = notify_url or f"https://catdog.dachaonet.com/api/orders/payments/{payment.id}/alipay/notify"
        
        # 执行请求
        response = self.alipay_client.sdk_execute(request)
        order_string = response
        
        return {
            "payment_id": payment.id,
            "order_string": order_string,
            "out_trade_no": out_trade_no,
            "total_amount": total_amount,
            "subject": subject
        }

    async def create_web_payment(
        self,
        db: Session,
        order_id: int,
        user_id: int,
        return_url: str = "http://localhost:3000/payment/success",
        notify_url: str = None
    ) -> str:
        """创建支付宝网页支付"""
        
        # 获取订单信息
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise ValueError("订单不存在")
            
        if order.buyer_id != user_id:
            raise ValueError("无权限支付此订单")
            
        if order.payment_status != 1:  # 1:待支付
            raise ValueError("订单状态不允许支付")

        # 生成商户订单号
        out_trade_no = f"ORDER_{order_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 订单信息
        subject = f"宠物拍卖订单-{order.order_no}"
        total_amount = str(order.total_amount)
        
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
        
        # 构建网页支付请求
        request = AlipayTradePagePayRequest()
        biz_content = {
            "out_trade_no": out_trade_no,
            "total_amount": total_amount,
            "subject": subject,
            "timeout_express": "30m"
        }
        request.biz_content = json.dumps(biz_content)
        request.return_url = return_url
        request.notify_url = notify_url or f"https://catdog.dachaonet.com/api/orders/payments/{payment.id}/alipay/notify"
        
        # 执行请求，获取完整的支付表单HTML
        response = self.alipay_client.page_execute(request, "GET")
        pay_url = response
        
        return pay_url

    async def verify_notify(self, notify_data: Dict[str, Any]) -> bool:
        """验证支付宝回调通知"""
        try:
            # 获取签名
            sign = notify_data.get("sign", "")
            if not sign:
                return False
            
            # 移除sign和sign_type参数
            verify_data = {k: v for k, v in notify_data.items() if k not in ["sign", "sign_type"]}
            
            # 验证签名
            return verify_with_rsa(settings.ALIPAY_PUBLIC_KEY, verify_data, sign)
        except Exception as e:
            print(f"验证支付宝通知失败: {e}")
            return False

    async def handle_notify(
        self,
        db: Session,
        payment_id: int,
        notify_data: Dict[str, Any]
    ) -> bool:
        """处理支付宝回调通知"""
        try:
            # 验证签名
            if not await self.verify_notify(notify_data):
                print("支付宝通知签名验证失败")
                return False
                
            payment = db.query(Payment).filter(Payment.id == payment_id).first()
            if not payment:
                print(f"支付记录不存在: {payment_id}")
                return False
                
            trade_status = notify_data.get("trade_status")
            out_trade_no = notify_data.get("out_trade_no")
            
            # 验证商户订单号
            if payment.transaction_id != out_trade_no:
                print(f"商户订单号不匹配: {payment.transaction_id} != {out_trade_no}")
                return False
            
            # 处理支付状态
            if trade_status in ["TRADE_SUCCESS", "TRADE_FINISHED"]:
                # 支付成功
                payment.status = "paid"
                payment.updated_at = datetime.now()
                
                # 更新订单状态
                order = db.query(Order).filter(Order.id == payment.order_id).first()
                if order:
                    order.payment_status = 2  # 已支付
                    order.order_status = 2  # 待发货
                    order.paid_at = datetime.now()
                
                db.commit()
                return True
                
            elif trade_status == "TRADE_CLOSED":
                # 交易关闭
                payment.status = "failed"
                payment.updated_at = datetime.now()
                db.commit()
                return True
                
            return False
            
        except Exception as e:
            print(f"处理支付宝通知失败: {e}")
            return False

    async def query_payment(self, out_trade_no: str) -> Dict[str, Any]:
        """查询支付状态"""
        try:
            request = AlipayTradeQueryRequest()
            biz_content = {"out_trade_no": out_trade_no}
            request.biz_content = json.dumps(biz_content)
            
            response = self.alipay_client.execute(request)
            return json.loads(response) if response else {}
        except Exception as e:
            print(f"查询支付状态失败: {e}")
            return {}

    async def close_payment(self, out_trade_no: str) -> bool:
        """关闭支付订单"""
        try:
            request = AlipayTradeCloseRequest()
            biz_content = {"out_trade_no": out_trade_no}
            request.biz_content = json.dumps(biz_content)
            
            response = self.alipay_client.execute(request)
            result = json.loads(response) if response else {}
            return result.get("code") == "10000"
        except Exception as e:
            print(f"关闭支付订单失败: {e}")
            return False

    async def refund(
        self,
        db: Session,
        payment_id: int,
        refund_amount: Decimal = None,
        refund_reason: str = "用户申请退款"
    ) -> Dict[str, Any]:
        """申请退款"""
        try:
            payment = db.query(Payment).filter(Payment.id == payment_id).first()
            if not payment:
                raise ValueError("支付记录不存在")
                
            if payment.status != "paid":
                raise ValueError("订单未支付，无法退款")
                
            # 退款金额默认为支付金额
            if refund_amount is None:
                refund_amount = payment.amount
                
            # 生成退款单号
            out_refund_no = f"REFUND_{payment_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # 调用支付宝退款接口
            request = AlipayTradeRefundRequest()
            biz_content = {
                "out_trade_no": payment.transaction_id,
                "refund_amount": str(refund_amount),
                "out_request_no": out_refund_no,
                "refund_reason": refund_reason
            }
            request.biz_content = json.dumps(biz_content)
            
            response = self.alipay_client.execute(request)
            result = json.loads(response) if response else {}
            
            if result.get("code") == "10000":
                # 退款成功，创建退款记录
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
            else:
                return {
                    "success": False,
                    "error": result.get("msg", "退款失败")
                }
                
        except Exception as e:
            print(f"退款失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }