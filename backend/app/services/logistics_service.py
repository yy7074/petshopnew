from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime
from decimal import Decimal

from ..models.order import Logistics, Order
from ..models.user import User
from ..schemas.order import LogisticsResponse
from ..core.config import settings

class LogisticsService:

    async def get_order_logistics(
        self,
        db: Session,
        order_id: int,
        user_id: int
    ) -> Optional[LogisticsResponse]:
        """获取订单物流信息"""
        # 验证权限
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return None

        if order.buyer_id != user_id and order.seller_id != user_id:
            raise ValueError("无权限查看此订单物流")

        logistics = db.query(Logistics).filter(Logistics.order_id == order_id).first()
        if not logistics:
            return None

        return LogisticsResponse(
            order_id=logistics.order_id,
            tracking_number=logistics.tracking_number,
            logistics_company=logistics.logistics_company,
            status=logistics.status,
            created_at=logistics.created_at,
            updated_at=logistics.updated_at
        )

    async def update_logistics(
        self,
        db: Session,
        order_id: int,
        tracking_number: str,
        logistics_company: str,
        user_id: int
    ) -> bool:
        """更新物流信息（卖家操作）"""
        # 验证订单和权限
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise ValueError("订单不存在")

        if order.seller_id != user_id:
            raise ValueError("只有卖家可以更新物流信息")

        if order.status not in ["paid", "shipped"]:
            raise ValueError("订单状态不允许发货")

        # 获取或创建物流记录
        logistics = db.query(Logistics).filter(Logistics.order_id == order_id).first()
        if not logistics:
            logistics = Logistics(
                order_id=order_id,
                tracking_number=tracking_number,
                logistics_company=logistics_company,
                status="shipped"
            )
            db.add(logistics)
        else:
            logistics.tracking_number = tracking_number
            logistics.logistics_company = logistics_company
            logistics.status = "shipped"
            logistics.updated_at = datetime.now()

        # 更新订单状态
        order.status = "shipped"  # 从字符串改为数字状态码
        order.shipped_at = datetime.now()

        db.commit()
        return True

    async def update_logistics_status(
        self,
        db: Session,
        order_id: int,
        status: str,
        tracking_info: Optional[Dict[str, Any]] = None
    ):
        """更新物流状态（通常由物流公司回调）"""
        try:
            logistics = db.query(Logistics).filter(Logistics.order_id == order_id).first()
            if not logistics:
                return

            # 更新物流状态
            logistics.status = status
            logistics.updated_at = datetime.now()

            # 如果有跟踪信息，可以保存到单独的表或字段中
            if tracking_info:
                # 这里可以扩展物流跟踪详情
                pass

            # 根据物流状态更新订单状态
            order = db.query(Order).filter(Order.id == order_id).first()
            if order:
                if status == "delivered":
                    order.status = "delivered"  # 从字符串改为数字状态码
                    order.received_at = datetime.now()
                elif status == "in_transit":
                    order.status = "shipped"

            db.commit()

        except Exception as e:
            print(f"更新物流状态失败: {e}")

    async def send_shipping_notification(
        self,
        db: Session,
        order_id: int
    ):
        """发送发货通知"""
        try:
            order = db.query(Order).filter(Order.id == order_id).first()
            if not order:
                return

            logistics = db.query(Logistics).filter(Logistics.order_id == order_id).first()
            if not logistics:
                return

            buyer = db.query(User).filter(User.id == order.buyer_id).first()
            if buyer:
                # 这里可以发送发货通知
                # await notification_service.send_notification(...)
                print(f"发送发货通知给买家 {buyer.username}: 订单 {order.order_number} 已发货")

        except Exception as e:
            print(f"发送发货通知失败: {e}")

    async def get_logistics_tracking(
        self,
        db: Session,
        tracking_number: str,
        logistics_company: str
    ) -> Dict[str, Any]:
        """获取物流跟踪信息（调用第三方物流API）"""
        try:
            # 这里实现调用第三方物流API的逻辑
            # 比如：顺丰、圆通、申通等物流公司的API

            # 暂时返回模拟数据
            return {
                "tracking_number": tracking_number,
                "logistics_company": logistics_company,
                "status": "in_transit",
                "tracking_details": [
                    {
                        "time": datetime.now().isoformat(),
                        "description": "包裹已到达【北京分拨中心】",
                        "location": "北京"
                    },
                    {
                        "time": (datetime.now().replace(hour=datetime.now().hour - 2)).isoformat(),
                        "description": "快件已从【深圳发货中心】发出",
                        "location": "深圳"
                    }
                ]
            }

        except Exception as e:
            print(f"获取物流跟踪信息失败: {e}")
            return {
                "tracking_number": tracking_number,
                "logistics_company": logistics_company,
                "status": "unknown",
                "error": "获取物流信息失败"
            }

    async def calculate_shipping_fee(
        self,
        weight: float,
        distance: float,
        shipping_type: str = "standard"
    ) -> Decimal:
        """计算运费"""
        from decimal import Decimal

        # 基础运费计算逻辑
        base_fee = Decimal("10.00")  # 基础运费

        # 按重量收费
        weight_fee = Decimal(str(weight)) * Decimal("2.00")

        # 按距离收费
        distance_fee = Decimal(str(distance)) * Decimal("0.50")

        # 快递类型加价
        type_multiplier = {
            "standard": Decimal("1.00"),
            "express": Decimal("1.50"),
            "next_day": Decimal("2.00")
        }

        total_fee = (base_fee + weight_fee + distance_fee) * type_multiplier.get(shipping_type, Decimal("1.00"))

        # 最低运费
        return max(total_fee, Decimal("8.00"))