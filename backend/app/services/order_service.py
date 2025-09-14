from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

from ..models.order import Order, OrderItem, Payment, Logistics
from ..models.product import Product, Bid
from ..models.user import User
from ..schemas.order import OrderCreate, OrderResponse, OrderListResponse, OrderUpdate
from ..core.config import settings

class OrderService:
    
    async def create_order(
        self, 
        db: Session, 
        order_data: OrderCreate, 
        user_id: int
    ) -> OrderResponse:
        """创建订单"""
        # 验证商品
        product = db.query(Product).filter(Product.id == order_data.product_id).first()
        if not product:
            raise ValueError("商品不存在")
        
        if product.seller_id == user_id:
            raise ValueError("不能购买自己的商品")
        
        if product.status not in ["active", "sold"]:
            raise ValueError("商品状态不允许购买")
        
        # 检查商品类型和购买方式
        if order_data.order_type == "auction":
            # 竞拍类商品需要检查是否中标
            winning_bid = db.query(Bid).filter(
                and_(
                    Bid.product_id == order_data.product_id,
                    Bid.user_id == user_id,
                    Bid.status == "won"
                )
            ).first()
            
            if not winning_bid:
                raise ValueError("您没有中标该商品")
            
            total_amount = winning_bid.amount
        
        elif order_data.order_type == "buy_now":
            # 一口价购买
            if product.auction_type != "fixed_price":
                raise ValueError("该商品不支持一口价购买")
            
            total_amount = product.current_price * order_data.quantity
        
        else:
            raise ValueError("无效的订单类型")
        
        # 检查库存
        if order_data.quantity > product.stock:
            raise ValueError("库存不足")
        
        # 生成订单号
        order_number = self._generate_order_number()
        
        # 创建订单
        order = Order(
            order_number=order_number,
            buyer_id=user_id,
            seller_id=product.seller_id,
            product_id=order_data.product_id,
            quantity=order_data.quantity,
            unit_price=product.current_price,
            total_amount=total_amount,
            order_type=order_data.order_type,
            payment_method=order_data.payment_method,
            shipping_address=order_data.shipping_address,
            buyer_note=order_data.buyer_note,
            status="pending"
        )
        
        db.add(order)
        db.commit()
        db.refresh(order)
        
        # 创建订单项
        order_item = OrderItem(
            order_id=order.id,
            product_id=order_data.product_id,
            product_title=product.title,
            product_image=product.images[0] if product.images else None,
            quantity=order_data.quantity,
            unit_price=product.current_price,
            total_price=total_amount
        )
        
        db.add(order_item)
        
        # 更新商品状态
        if order_data.order_type == "auction" or product.auction_type == "fixed_price":
            product.status = "sold"
            product.stock -= order_data.quantity
        
        db.commit()
        
        return self._to_order_response(order, db)
    
    async def get_user_orders(
        self, 
        db: Session, 
        user_id: int, 
        page: int = 1, 
        page_size: int = 20,
        status: Optional[str] = None,
        order_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> OrderListResponse:
        """获取用户订单列表"""
        # 根据order_type决定查询买家还是卖家订单
        if order_type == "buy":
            query = db.query(Order).filter(Order.buyer_id == user_id)
        elif order_type == "sell":
            query = db.query(Order).filter(Order.seller_id == user_id)
        else:
            # 默认查询买家订单
            query = db.query(Order).filter(Order.buyer_id == user_id)
        
        # 状态筛选 - 将字符串状态转换为数字状态
        if status:
            status_mapping = {
                'pending': 1,    # 待支付
                'paid': 2,       # 待发货  
                'shipped': 3,    # 已发货
                'delivered': 4,  # 已收货
                'completed': 5,  # 已完成
                'cancelled': 6,  # 已取消
                'refunded': 3    # 已退款 (使用payment_status=3)
            }
            
            if status == 'refunded':
                query = query.filter(Order.payment_status == 3)
            else:
                order_status = status_mapping.get(status)
                if order_status:
                    query = query.filter(Order.order_status == order_status)
        
        # 时间范围筛选
        if start_date:
            query = query.filter(Order.created_at >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(Order.created_at <= datetime.fromisoformat(end_date))
        
        query = query.order_by(desc(Order.created_at))
        
        # 分页
        total = query.count()
        offset = (page - 1) * page_size
        orders = query.offset(offset).limit(page_size).all()
        
        return OrderListResponse(
            items=[self._to_order_response(order, db) for order in orders],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )
    
    async def get_order_detail(
        self, 
        db: Session, 
        order_id: int, 
        user_id: int
    ) -> Optional[OrderResponse]:
        """获取订单详情"""
        order = db.query(Order).filter(
            and_(
                Order.id == order_id,
                or_(Order.buyer_id == user_id, Order.seller_id == user_id)
            )
        ).first()
        
        if not order:
            return None
        
        return self._to_order_response(order, db)
    
    async def update_order(
        self, 
        db: Session, 
        order_id: int, 
        order_data: OrderUpdate, 
        user_id: int
    ) -> Optional[OrderResponse]:
        """更新订单"""
        order = db.query(Order).filter(
            and_(
                Order.id == order_id,
                or_(Order.buyer_id == user_id, Order.seller_id == user_id)
            )
        ).first()
        
        if not order:
            return None
        
        # 只允许特定字段更新
        allowed_fields = ["shipping_address", "buyer_note", "seller_note"]
        update_data = order_data.dict(include=set(allowed_fields), exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(order, field, value)
        
        order.updated_at = datetime.now()
        db.commit()
        
        return self._to_order_response(order, db)
    
    async def update_order_status(
        self, 
        db: Session, 
        order_id: int, 
        status: str, 
        user_id: int
    ) -> bool:
        """更新订单状态"""
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return False
        
        # 权限检查
        if status in ["shipped", "delivered"] and order.seller_id != user_id:
            raise ValueError("只有卖家可以更新发货状态")
        
        if status in ["completed", "cancelled"] and order.buyer_id != user_id:
            raise ValueError("只有买家可以确认收货或取消订单")
        
        # 状态流转检查
        valid_transitions = {
            "pending": ["paid", "cancelled"],
            "paid": ["shipped", "cancelled"],
            "shipped": ["delivered", "completed"],
            "delivered": ["completed"],
            "completed": [],
            "cancelled": ["refunded"],
            "refunded": []
        }
        
        if status not in valid_transitions.get(order.status, []):
            raise ValueError(f"不能从状态 {order.status} 转换到 {status}")
        
        order.status = status
        order.updated_at = datetime.now()
        
        # 状态相关的特殊处理
        if status == "completed":
            order.completed_at = datetime.now()
        elif status == "shipped":
            order.shipped_at = datetime.now()
        elif status == "cancelled":
            order.cancelled_at = datetime.now()
        
        db.commit()
        return True
    
    async def cancel_order(
        self, 
        db: Session, 
        order_id: int, 
        user_id: int, 
        reason: Optional[str] = None
    ) -> bool:
        """取消订单"""
        order = db.query(Order).filter(
            and_(
                Order.id == order_id,
                Order.buyer_id == user_id
            )
        ).first()
        
        if not order:
            return False
        
        # 只有待付款和已付款状态可以取消
        if order.status not in ["pending", "paid"]:
            raise ValueError("该订单状态不允许取消")
        
        order.status = "cancelled"
        order.cancelled_at = datetime.now()
        order.cancel_reason = reason
        order.updated_at = datetime.now()
        
        # 恢复商品状态和库存
        product = db.query(Product).filter(Product.id == order.product_id).first()
        if product:
            if order.order_type == "auction":
                product.status = "active"  # 重新开放竞拍
            product.stock += order.quantity
        
        db.commit()
        return True
    
    async def confirm_order(
        self, 
        db: Session, 
        order_id: int, 
        user_id: int
    ) -> bool:
        """确认收货"""
        order = db.query(Order).filter(
            and_(
                Order.id == order_id,
                Order.buyer_id == user_id
            )
        ).first()
        
        if not order:
            return False
        
        if order.status not in ["shipped", "delivered"]:
            raise ValueError("订单状态不允许确认收货")
        
        order.status = "completed"
        order.completed_at = datetime.now()
        order.updated_at = datetime.now()
        
        db.commit()
        return True
    
    async def get_user_order_statistics(
        self, 
        db: Session, 
        user_id: int, 
        period: str = "month"
    ) -> Dict[str, Any]:
        """获取用户订单统计"""
        # 计算时间范围
        if period == "week":
            start_date = datetime.now() - timedelta(weeks=1)
        elif period == "month":
            start_date = datetime.now() - timedelta(days=30)
        elif period == "quarter":
            start_date = datetime.now() - timedelta(days=90)
        elif period == "year":
            start_date = datetime.now() - timedelta(days=365)
        else:
            start_date = datetime.now() - timedelta(days=30)
        
        # 买家统计
        buyer_stats = db.query(
            func.count(Order.id).label("total_orders"),
            func.sum(Order.total_amount).label("total_amount"),
            func.count(func.case([(Order.status == "completed", 1)])).label("completed_orders")
        ).filter(
            and_(
                Order.buyer_id == user_id,
                Order.created_at >= start_date
            )
        ).first()
        
        # 卖家统计
        seller_stats = db.query(
            func.count(Order.id).label("total_sales"),
            func.sum(Order.total_amount).label("total_revenue"),
            func.count(func.case([(Order.status == "completed", 1)])).label("completed_sales")
        ).filter(
            and_(
                Order.seller_id == user_id,
                Order.created_at >= start_date
            )
        ).first()
        
        # 状态分布
        status_distribution = db.query(
            Order.status,
            func.count(Order.id).label("count")
        ).filter(
            and_(
                or_(Order.buyer_id == user_id, Order.seller_id == user_id),
                Order.created_at >= start_date
            )
        ).group_by(Order.status).all()
        
        return {
            "period": period,
            "buyer_stats": {
                "total_orders": buyer_stats.total_orders or 0,
                "total_amount": float(buyer_stats.total_amount or 0),
                "completed_orders": buyer_stats.completed_orders or 0,
                "completion_rate": (buyer_stats.completed_orders or 0) / max(buyer_stats.total_orders or 1, 1)
            },
            "seller_stats": {
                "total_sales": seller_stats.total_sales or 0,
                "total_revenue": float(seller_stats.total_revenue or 0),
                "completed_sales": seller_stats.completed_sales or 0,
                "completion_rate": (seller_stats.completed_sales or 0) / max(seller_stats.total_sales or 1, 1)
            },
            "status_distribution": [
                {"status": status.status, "count": status.count}
                for status in status_distribution
            ]
        }
    
    async def send_order_notification(
        self, 
        db: Session, 
        order_id: int, 
        notification_type: str
    ):
        """发送订单通知（后台任务）"""
        # 这里实现通知逻辑（短信、推送等）
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return
        
        # 获取买家和卖家信息
        buyer = db.query(User).filter(User.id == order.buyer_id).first()
        seller = db.query(User).filter(User.id == order.seller_id).first()
        
        # 根据通知类型发送不同的消息
        notification_messages = {
            "created": f"您的订单 {order.order_number} 已创建，请及时付款",
            "paid": f"您有新的订单 {order.order_number}，请及时发货",
            "shipped": f"您的订单 {order.order_number} 已发货，请注意查收",
            "completed": f"您的订单 {order.order_number} 已完成，感谢您的购买",
            "cancelled": f"您的订单 {order.order_number} 已取消"
        }
        
        message = notification_messages.get(notification_type, "订单状态已更新")
        
        # 实际发送通知的逻辑
        # await send_sms(buyer.phone, message)
        # await send_push_notification(buyer.id, message)
        
        print(f"发送通知给用户 {buyer.username}: {message}")
    
    async def process_order_cancellation(
        self, 
        db: Session, 
        order_id: int
    ):
        """处理订单取消的后续流程（后台任务）"""
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return
        
        # 如果已付款，处理退款
        if order.status == "paid":
            payment = db.query(Payment).filter(Payment.order_id == order_id).first()
            if payment:
                # 创建退款记录
                refund = Payment(
                    order_id=order_id,
                    user_id=order.buyer_id,
                    payment_method=payment.payment_method,
                    amount=-payment.amount,  # 负数表示退款
                    payment_type="refund",
                    status="processing",
                    transaction_id=f"refund_{payment.transaction_id}"
                )
                db.add(refund)
                db.commit()
                
                # 调用支付接口处理退款
                # await process_refund(payment.transaction_id, payment.amount)
        
        print(f"处理订单 {order.order_number} 取消流程完成")
    
    async def complete_order_process(
        self, 
        db: Session, 
        order_id: int
    ):
        """完成订单的后续处理（后台任务）"""
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return
        
        # 处理资金结算
        # 将订单金额转给卖家（扣除平台手续费）
        platform_fee_rate = 0.05  # 5% 平台手续费
        platform_fee = order.total_amount * Decimal(platform_fee_rate)
        seller_amount = order.total_amount - platform_fee
        
        # 更新卖家余额
        seller = db.query(User).filter(User.id == order.seller_id).first()
        if seller:
            seller.balance += seller_amount
        
        # 更新买卖双方评分权限
        # 这里可以创建评价记录等
        
        db.commit()
        print(f"订单 {order.order_number} 完成处理，卖家收到 {seller_amount} 元")
    
    def _generate_order_number(self) -> str:
        """生成订单号"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = str(uuid.uuid4().int)[:6]
        return f"PET{timestamp}{random_suffix}"
    
    def _to_order_response(self, order: Order, db: Session) -> OrderResponse:
        """转换为响应格式"""
        # 获取订单项
        order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        
        # 获取买家和卖家信息
        buyer = db.query(User).filter(User.id == order.buyer_id).first()
        seller = db.query(User).filter(User.id == order.seller_id).first()
        
        # 获取商品信息
        product = db.query(Product).filter(Product.id == order.product_id).first()
        
        # 获取支付信息
        payment = db.query(Payment).filter(Payment.order_id == order.id).first()
        
        # 获取物流信息
        logistics = db.query(Logistics).filter(Logistics.order_id == order.id).first()
        
        return OrderResponse(
            id=order.id,
            order_no=order.order_no,
            buyer_id=order.buyer_id,
            seller_id=order.seller_id,
            product_id=order.product_id,
            quantity=1,  # 从订单项中获取或默认为1
            order_type="auction",  # 从商品信息中获取
            final_price=order.final_price,
            shipping_fee=order.shipping_fee or Decimal('0.00'),
            total_amount=order.total_amount,
            payment_method=order.payment_method,
            payment_status=order.payment_status,
            order_status=order.order_status,
            shipping_address=order.shipping_address,
            tracking_number=order.tracking_number,
            shipped_at=order.shipped_at,
            received_at=order.received_at,
            completed_at=order.completed_at,
            created_at=order.created_at,
            updated_at=order.updated_at,
            items=[
                {
                    "id": item.id,
                    "product_id": item.product_id,
                    "product_title": item.product_title,
                    "product_image": item.product_image,
                    "quantity": item.quantity,
                    "unit_price": float(item.unit_price),
                    "total_price": float(item.total_price)
                }
                for item in order_items
            ],
            buyer_info={
                "id": buyer.id,
                "username": buyer.username,
                "nickname": getattr(buyer, 'nickname', buyer.username),
                "avatar": buyer.avatar
            } if buyer else None,
            seller_info={
                "id": seller.id,
                "username": seller.username,
                "nickname": getattr(seller, 'nickname', seller.username),
                "avatar": getattr(seller, 'avatar', None)
            } if seller else None,
            product_info={
                "id": product.id,
                "title": product.title,
                "images": product.images or [],
                "category": product.category,
                "seller_id": product.seller_id
            } if product else None,
            payment_info={
                "payment_id": payment.id,
                "status": payment.status,
                "transaction_id": payment.transaction_id,
                "payment_method": payment.payment_method,
                "amount": float(payment.amount)
            } if payment else None,
            logistics_info={
                "tracking_number": logistics.tracking_number,
                "logistics_company": logistics.logistics_company,
                "status": logistics.status,
                "updated_at": logistics.updated_at
            } if logistics else None
        )