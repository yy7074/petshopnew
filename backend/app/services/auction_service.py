from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
import asyncio
import logging

from ..models.product import Product, Bid
from ..models.order import Order, OrderItem
from ..models.user import User
from ..core.database import get_db
from .notification_service import NotificationService

logger = logging.getLogger(__name__)

class AuctionService:
    """拍卖管理服务"""
    
    def __init__(self):
        self.notification_service = NotificationService()
    
    async def check_and_end_auctions(self, db: Session) -> List[Dict[str, Any]]:
        """检查并结束已到期的拍卖"""
        current_time = datetime.now()
        
        # 查找已到期但状态还是拍卖中的商品
        expired_auctions = db.query(Product).filter(
            and_(
                Product.auction_end_time <= current_time,
                Product.status == 2  # 拍卖中
            )
        ).all()
        
        results = []
        
        for product in expired_auctions:
            try:
                result = await self._process_auction_end(db, product)
                results.append(result)
            except Exception as e:
                logger.error(f"处理拍卖结束失败，商品ID: {product.id}, 错误: {e}")
                results.append({
                    "product_id": product.id,
                    "success": False,
                    "error": str(e)
                })
        
        return results
    
    async def _process_auction_end(self, db: Session, product: Product) -> Dict[str, Any]:
        """处理单个拍卖结束"""
        
        # 查找最高出价
        winning_bid = db.query(Bid).filter(
            Bid.product_id == product.id
        ).order_by(desc(Bid.bid_amount)).first()
        
        if winning_bid:
            # 有人出价，创建获胜者订单
            order = await self._create_auction_winner_order(db, product, winning_bid)
            
            # 更新出价状态
            db.query(Bid).filter(
                Bid.product_id == product.id,
                Bid.id == winning_bid.id
            ).update({"status": 1})  # 1: 获胜
            
            # 其他出价状态改为失败
            db.query(Bid).filter(
                and_(
                    Bid.product_id == product.id,
                    Bid.id != winning_bid.id,
                    Bid.status != 3  # 不是已撤销的
                )
            ).update({"status": 2})  # 2: 被超越/失败
            
            # 更新商品状态为已结束
            product.status = 3  # 已结束
            
            # 发送通知给获胜者
            await self._send_auction_winner_notification(db, product, winning_bid, order)
            
            # 发送通知给失败的竞拍者
            await self._send_auction_loser_notifications(db, product, winning_bid.bidder_id)
            
            db.commit()
            
            return {
                "product_id": product.id,
                "success": True,
                "winner_id": winning_bid.bidder_id,
                "winning_amount": str(winning_bid.bid_amount),
                "order_id": order.id,
                "order_no": order.order_no
            }
        else:
            # 流拍，无人出价
            product.status = 3  # 已结束
            db.commit()
            
            # 通知卖家流拍
            await self._send_auction_failed_notification(db, product)
            
            return {
                "product_id": product.id,
                "success": True,
                "winner_id": None,
                "winning_amount": None,
                "order_id": None,
                "message": "流拍"
            }
    
    async def _create_auction_winner_order(
        self, 
        db: Session, 
        product: Product, 
        winning_bid: Bid
    ) -> Order:
        """为拍卖获胜者创建订单"""
        
        # 生成订单号
        order_no = f"AUCTION_{product.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 创建订单
        order = Order(
            order_no=order_no,
            buyer_id=winning_bid.bidder_id,
            seller_id=product.seller_id,
            product_id=product.id,
            final_price=winning_bid.bid_amount,
            shipping_fee=product.shipping_fee or Decimal("0.00"),
            total_amount=winning_bid.bid_amount + (product.shipping_fee or Decimal("0.00")),
            payment_method=1,  # 默认支付宝
            payment_status=1,  # 待支付
            order_status=1,    # 待支付
            shipping_address={}  # 待买家补充
        )
        
        db.add(order)
        db.flush()  # 获取order.id
        
        # 创建订单项
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            product_title=product.title,
            product_image=product.images[0] if product.images else None,
            quantity=1,  # 拍卖商品数量为1
            unit_price=winning_bid.bid_amount,
            total_price=winning_bid.bid_amount
        )
        
        db.add(order_item)
        
        return order
    
    async def _send_auction_winner_notification(
        self, 
        db: Session, 
        product: Product, 
        winning_bid: Bid, 
        order: Order
    ):
        """发送获胜通知"""
        try:
            winner = db.query(User).filter(User.id == winning_bid.bidder_id).first()
            if winner:
                await self.notification_service.send_auction_winner_notification(
                    db=db,
                    user_id=winner.id,
                    product_title=product.title,
                    winning_amount=str(winning_bid.bid_amount),
                    order_id=order.id
                )
        except Exception as e:
            logger.error(f"发送获胜通知失败: {e}")
    
    async def _send_auction_loser_notifications(
        self, 
        db: Session, 
        product: Product, 
        winner_id: int
    ):
        """发送失败通知给其他竞拍者"""
        try:
            # 获取所有其他竞拍者
            losers = db.query(User).join(Bid).filter(
                and_(
                    Bid.product_id == product.id,
                    Bid.bidder_id != winner_id,
                    Bid.status != 3  # 不是撤销的出价
                )
            ).distinct().all()
            
            for loser in losers:
                await self.notification_service.send_auction_loser_notification(
                    db=db,
                    user_id=loser.id,
                    product_title=product.title
                )
        except Exception as e:
            logger.error(f"发送失败通知失败: {e}")
    
    async def _send_auction_failed_notification(
        self, 
        db: Session, 
        product: Product
    ):
        """发送流拍通知给卖家"""
        try:
            await self.notification_service.send_auction_failed_notification(
                db=db,
                user_id=product.seller_id,
                product_title=product.title
            )
        except Exception as e:
            logger.error(f"发送流拍通知失败: {e}")
    
    async def manual_end_auction(
        self, 
        db: Session, 
        product_id: int, 
        seller_id: int
    ) -> Dict[str, Any]:
        """手动结束拍卖（卖家操作）"""
        
        product = db.query(Product).filter(
            and_(
                Product.id == product_id,
                Product.seller_id == seller_id,
                Product.status == 2  # 拍卖中
            )
        ).first()
        
        if not product:
            raise ValueError("商品不存在或无权限操作")
        
        return await self._process_auction_end(db, product)
    
    async def get_auction_status(
        self, 
        db: Session, 
        product_id: int
    ) -> Dict[str, Any]:
        """获取拍卖状态"""
        
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError("商品不存在")
        
        # 获取当前最高出价
        current_bid = db.query(Bid).filter(
            Bid.product_id == product_id
        ).order_by(desc(Bid.bid_amount)).first()
        
        # 获取出价数量
        bid_count = db.query(func.count(Bid.id)).filter(
            Bid.product_id == product_id
        ).scalar()
        
        # 检查是否已结束
        is_ended = product.auction_end_time and product.auction_end_time <= datetime.now()
        
        return {
            "product_id": product_id,
            "status": product.status,
            "current_price": str(product.current_price),
            "highest_bid": str(current_bid.bid_amount) if current_bid else None,
            "bid_count": bid_count,
            "start_time": product.auction_start_time.isoformat() if product.auction_start_time else None,
            "end_time": product.auction_end_time.isoformat() if product.auction_end_time else None,
            "is_ended": is_ended,
            "time_remaining": self._calculate_time_remaining(product.auction_end_time) if not is_ended else None
        }
    
    def _calculate_time_remaining(self, end_time: datetime) -> Dict[str, int]:
        """计算剩余时间"""
        if not end_time:
            return None
        
        now = datetime.now()
        if end_time <= now:
            return {"days": 0, "hours": 0, "minutes": 0, "seconds": 0}
        
        remaining = end_time - now
        days = remaining.days
        hours, remainder = divmod(remaining.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        return {
            "days": days,
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds
        }