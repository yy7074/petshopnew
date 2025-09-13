from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..models.user import User
from ..models.order import Message
from ..core.config import settings

class NotificationService:

    async def send_bid_notification(
        self,
        db: Session,
        product_id: int,
        bid_amount: float,
        bidder_username: str
    ):
        """发送出价通知"""
        try:
            # 这里实现实际的通知逻辑，比如推送、短信等
            # 暂时只保存到数据库消息表

            # 获取商品信息
            from ..models.product import Product
            product = db.query(Product).filter(Product.id == product_id).first()
            if not product:
                return

            # 获取卖家信息
            seller = db.query(User).filter(User.id == product.seller_id).first()
            if seller:
                # 创建消息通知
                message = Message(
                    sender_id=None,  # 系统消息
                    receiver_id=seller.id,
                    message_type=3,  # 拍卖通知
                    title="新的竞拍出价",
                    content=f"您的商品 '{product.title}' 收到新的出价 ¥{bid_amount}，出价人：{bidder_username}",
                    related_id=product_id
                )
                db.add(message)
                db.commit()

                # 这里可以添加推送通知逻辑
                # await self._send_push_notification(seller.id, message.title, message.content)

        except Exception as e:
            print(f"发送出价通知失败: {e}")
            # 不抛出异常，避免影响出价流程

    async def send_order_notification(
        self,
        db: Session,
        order_id: int,
        notification_type: str
    ):
        """发送订单通知"""
        try:
            # 获取订单信息
            from ..models.order import Order
            order = db.query(Order).filter(Order.id == order_id).first()
            if not order:
                return

            # 获取买家和卖家信息
            buyer = db.query(User).filter(User.id == order.buyer_id).first()
            seller = db.query(User).filter(User.id == order.seller_id).first()

            # 根据通知类型发送不同消息
            if notification_type == "created":
                # 订单创建通知 - 发给买家
                if buyer:
                    message = Message(
                        sender_id=None,
                        receiver_id=buyer.id,
                        message_type=4,  # 订单通知
                        title="订单创建成功",
                        content=f"您的订单 {order.order_number} 已创建成功，请及时付款",
                        related_id=order_id
                    )
                    db.add(message)
                    db.commit()

            elif notification_type == "paid":
                # 付款成功通知 - 发给卖家
                if seller:
                    message = Message(
                        sender_id=None,
                        receiver_id=seller.id,
                        message_type=4,
                        title="收到新订单",
                        content=f"您的商品收到新订单 {order.order_number}，买家已付款，请及时发货",
                        related_id=order_id
                    )
                    db.add(message)
                    db.commit()

            elif notification_type == "shipped":
                # 发货通知 - 发给买家
                if buyer:
                    message = Message(
                        sender_id=None,
                        receiver_id=buyer.id,
                        message_type=4,
                        title="商品已发货",
                        content=f"您的订单 {order.order_number} 已发货，请注意查收",
                        related_id=order_id
                    )
                    db.add(message)
                    db.commit()

            elif notification_type == "completed":
                # 订单完成通知 - 发给买家
                if buyer:
                    message = Message(
                        sender_id=None,
                        receiver_id=buyer.id,
                        message_type=4,
                        title="订单已完成",
                        content=f"您的订单 {order.order_number} 已完成，感谢您的购买",
                        related_id=order_id
                    )
                    db.add(message)
                    db.commit()

            elif notification_type == "cancelled":
                # 订单取消通知 - 发给买家和卖家
                for user in [buyer, seller]:
                    if user:
                        message = Message(
                            sender_id=None,
                            receiver_id=user.id,
                            message_type=4,
                            title="订单已取消",
                            content=f"您的订单 {order.order_number} 已取消",
                            related_id=order_id
                        )
                        db.add(message)
                db.commit()

        except Exception as e:
            print(f"发送订单通知失败: {e}")
            # 不抛出异常，避免影响订单流程

    async def send_system_notification(
        self,
        db: Session,
        user_ids: List[int],
        title: str,
        content: str,
        related_id: Optional[int] = None
    ):
        """发送系统通知"""
        try:
            for user_id in user_ids:
                message = Message(
                    sender_id=None,
                    receiver_id=user_id,
                    message_type=1,  # 系统消息
                    title=title,
                    content=content,
                    related_id=related_id
                )
                db.add(message)
            db.commit()
        except Exception as e:
            print(f"发送系统通知失败: {e}")

    async def _send_push_notification(self, user_id: int, title: str, content: str):
        """发送推送通知（占位符）"""
        # 这里实现实际的推送逻辑，比如：
        # - Firebase Cloud Messaging
        # - 极光推送
        # - 微信小程序推送等
        print(f"推送通知到用户 {user_id}: {title} - {content}")