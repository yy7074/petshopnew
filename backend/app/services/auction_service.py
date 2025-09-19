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
from ..models.deposit import Deposit
from ..core.database import get_db
from .notification_service import NotificationService

logger = logging.getLogger(__name__)

class AuctionService:
    """拍卖管理服务"""
    
    # 拍卖标准化规则
    AUCTION_RULES = {
        "min_bid_increment": Decimal("1.00"),  # 最小加价幅度
        "auto_extend_time": 300,  # 自动延时5分钟（秒）
        "extend_threshold": 300,  # 结束前5分钟内有出价则延时
        "max_extensions": 3,  # 最多延时3次
        "min_auction_duration": 3600,  # 最短拍卖时长1小时
        "max_auction_duration": 604800,  # 最长拍卖时长7天
        "deposit_rate": Decimal("0.1"),  # 保证金比例10%
    }
    
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
        
        # 如果拍卖已结束但状态还是拍卖中，自动更新状态
        if is_ended and product.status == 2:  # 2表示拍卖中
            await self._auto_end_auction(db, product)
        
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
    
    async def _auto_end_auction(self, db: Session, product: Product):
        """自动结束拍卖并设置获胜者"""
        try:
            logger.info(f"自动结束拍卖: 商品ID {product.id}")
            
            # 更新商品状态为已结束
            product.status = 3  # 已结束
            
            # 查找最高出价
            highest_bid = db.query(Bid).filter(
                Bid.product_id == product.id
            ).order_by(desc(Bid.bid_amount)).first()
            
            if highest_bid:
                # 设置获胜出价
                highest_bid.status = 1  # 获胜
                
                # 将其他出价设置为失败
                other_bids = db.query(Bid).filter(
                    Bid.product_id == product.id,
                    Bid.id != highest_bid.id
                ).all()
                
                for bid in other_bids:
                    bid.status = 2  # 失败
                
                logger.info(f"拍卖结束: 商品 {product.id}, 获胜者 {highest_bid.bidder_id}, 成交价 ¥{highest_bid.bid_amount}")
                
                # 创建订单（如果需要）
                await self._create_winner_order(db, product, highest_bid)
            else:
                logger.info(f"拍卖流拍: 商品 {product.id}, 无人出价")
            
            db.commit()
            
        except Exception as e:
            logger.error(f"自动结束拍卖失败: 商品 {product.id}, 错误: {str(e)}")
            db.rollback()
            raise
    
    async def _create_winner_order(self, db: Session, product: Product, winning_bid: Bid):
        """为获胜者创建订单"""
        try:
            # 检查是否已存在订单
            existing_order = db.query(Order).filter(
                and_(
                    Order.product_id == product.id,
                    Order.buyer_id == winning_bid.bidder_id
                )
            ).first()
            
            if existing_order:
                logger.info(f"订单已存在: {existing_order.order_no}")
                return
            
            # 生成订单号
            import uuid
            order_no = f"A{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:6].upper()}"
            
            # 创建新订单
            order = Order(
                order_no=order_no,
                buyer_id=winning_bid.bidder_id,
                seller_id=product.seller_id,
                product_id=product.id,
                total_amount=winning_bid.bid_amount,
                payment_status=1,  # 待支付
                order_status=1,    # 待支付
                order_type=2,      # 拍卖订单
                created_at=datetime.now()
            )
            
            db.add(order)
            logger.info(f"创建拍卖订单: {order_no}, 金额: ¥{winning_bid.bid_amount}")
            
        except Exception as e:
            logger.error(f"创建获胜者订单失败: {str(e)}")
            # 不抛出异常，因为订单创建失败不应该影响拍卖结束
    
    async def validate_auction_setup(
        self, 
        db: Session, 
        auction_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """验证拍卖设置是否符合标准"""
        errors = []
        
        # 验证拍卖时长
        start_time = auction_data.get('auction_start_time')
        end_time = auction_data.get('auction_end_time')
        
        if start_time and end_time:
            duration = (end_time - start_time).total_seconds()
            if duration < self.AUCTION_RULES["min_auction_duration"]:
                errors.append(f"拍卖时长不能少于{self.AUCTION_RULES['min_auction_duration']//3600}小时")
            if duration > self.AUCTION_RULES["max_auction_duration"]:
                errors.append(f"拍卖时长不能超过{self.AUCTION_RULES['max_auction_duration']//86400}天")
        
        # 验证起拍价
        starting_price = auction_data.get('starting_price', 0)
        if starting_price <= 0:
            errors.append("起拍价必须大于0")
        
        # 验证最小加价幅度
        min_increment = auction_data.get('min_bid_increment', self.AUCTION_RULES["min_bid_increment"])
        if min_increment < self.AUCTION_RULES["min_bid_increment"]:
            errors.append(f"最小加价幅度不能小于{self.AUCTION_RULES['min_bid_increment']}元")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "normalized_data": self._normalize_auction_data(auction_data)
        }
    
    def _normalize_auction_data(self, auction_data: Dict[str, Any]) -> Dict[str, Any]:
        """标准化拍卖数据"""
        normalized = auction_data.copy()
        
        # 设置默认最小加价幅度
        if 'min_bid_increment' not in normalized:
            normalized['min_bid_increment'] = self.AUCTION_RULES["min_bid_increment"]
        
        # 确保最小加价幅度不低于标准
        min_increment = max(
            normalized.get('min_bid_increment', self.AUCTION_RULES["min_bid_increment"]),
            self.AUCTION_RULES["min_bid_increment"]
        )
        normalized['min_bid_increment'] = min_increment
        
        # 设置自动延时参数
        normalized['auto_extend_enabled'] = True
        normalized['extend_threshold'] = self.AUCTION_RULES["extend_threshold"]
        normalized['auto_extend_time'] = self.AUCTION_RULES["auto_extend_time"]
        normalized['max_extensions'] = self.AUCTION_RULES["max_extensions"]
        
        return normalized
    
    async def process_bid_with_auto_extend(
        self, 
        db: Session, 
        product_id: int, 
        bid_amount: Decimal,
        bidder_id: int
    ) -> Dict[str, Any]:
        """处理出价并检查是否需要自动延时"""
        
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError("商品不存在")
        
        if product.status != 2:  # 不是拍卖中状态
            raise ValueError("拍卖已结束或未开始")
        
        # 检查拍卖是否实际已过期
        if product.auction_end_time and product.auction_end_time <= datetime.now():
            raise ValueError("拍卖已结束，无法出价")
        
        # 检查保证金（如果需要）
        await self._check_bidder_deposit(db, bidder_id, product_id)
        
        # 检查出价是否有效
        current_highest = db.query(Bid).filter(
            Bid.product_id == product_id
        ).order_by(desc(Bid.bid_amount)).first()
        
        # 使用商品设置的最小加价幅度或全局规则
        min_increment = product.min_bid_increment or self.AUCTION_RULES["min_bid_increment"]
        min_required = product.current_price + min_increment
        
        if current_highest:
            min_required = current_highest.bid_amount + min_increment
        
        if bid_amount < min_required:
            raise ValueError(f"出价不能低于{min_required}元")
        
        # 创建出价记录
        new_bid = Bid(
            product_id=product_id,
            bidder_id=bidder_id,
            bid_amount=bid_amount,
            status=1
        )
        db.add(new_bid)
        
        # 更新之前的出价状态
        if current_highest:
            current_highest.status = 2  # 被超越
        
        # 更新商品当前价格
        product.current_price = bid_amount
        product.bid_count = (product.bid_count or 0) + 1
        
        # 检查是否需要自动延时
        auto_extended = False
        extension_minutes = 0
        
        if product.auction_end_time:
            time_remaining = (product.auction_end_time - datetime.now()).total_seconds()
            
            # 如果在结束前阈值时间内有出价，且未超过最大延时次数
            if (time_remaining <= self.AUCTION_RULES["extend_threshold"] and 
                time_remaining > 0 and
                (product.extension_count or 0) < self.AUCTION_RULES["max_extensions"]):
                
                # 延长拍卖时间
                product.auction_end_time = product.auction_end_time + timedelta(
                    seconds=self.AUCTION_RULES["auto_extend_time"]
                )
                
                # 更新延时计数
                product.extension_count = (product.extension_count or 0) + 1
                
                auto_extended = True
                extension_minutes = self.AUCTION_RULES["auto_extend_time"] // 60
                
                logger.info(f"拍卖{product_id}自动延时{extension_minutes}分钟，第{product.extension_count}次延时")
        
        db.commit()
        
        # 发送通知
        await self._send_bid_notifications(db, product, new_bid, auto_extended)
        
        return {
            "success": True,
            "bid_id": new_bid.id,
            "current_price": str(bid_amount),
            "auto_extended": auto_extended,
            "extension_minutes": extension_minutes,
            "extension_count": product.extension_count,
            "new_end_time": product.auction_end_time.isoformat() if product.auction_end_time else None
        }
    
    async def _send_bid_notifications(
        self, 
        db: Session, 
        product: Product, 
        new_bid: Bid, 
        auto_extended: bool
    ):
        """发送出价相关通知"""
        try:
            # 通知卖家有新出价
            await self.notification_service.send_new_bid_notification(
                db=db,
                user_id=product.seller_id,
                product_title=product.title,
                bid_amount=str(new_bid.bid_amount),
                auto_extended=auto_extended
            )
            
            # 通知被超越的竞拍者
            previous_bidders = db.query(User).join(Bid).filter(
                and_(
                    Bid.product_id == product.id,
                    Bid.bidder_id != new_bid.bidder_id,
                    Bid.status == 2  # 被超越
                )
            ).distinct().all()
            
            for bidder in previous_bidders:
                await self.notification_service.send_bid_outbid_notification(
                    db=db,
                    user_id=bidder.id,
                    product_title=product.title,
                    new_bid_amount=str(new_bid.bid_amount)
                )
                
        except Exception as e:
            logger.error(f"发送出价通知失败: {e}")
    
    async def get_auction_rules(self) -> Dict[str, Any]:
        """获取拍卖标准化规则"""
        return {
            "rules": self.AUCTION_RULES,
            "description": {
                "min_bid_increment": "每次加价不得少于此金额",
                "auto_extend_time": "自动延时的时长（秒）",
                "extend_threshold": "结束前多少秒内有出价将触发延时",
                "max_extensions": "单次拍卖最多可延时次数",
                "min_auction_duration": "拍卖最短持续时间（秒）",
                "max_auction_duration": "拍卖最长持续时间（秒）",
                "deposit_rate": "参与拍卖需要缴纳的保证金比例"
            }
        }
    
    async def _check_bidder_deposit(self, db: Session, bidder_id: int, product_id: int):
        """检查竞拍者保证金状态"""
        try:
            # 查找该用户在此拍卖的保证金
            deposit = db.query(Deposit).filter(
                and_(
                    Deposit.user_id == bidder_id,
                    Deposit.auction_id == product_id,
                    Deposit.status == "active"
                )
            ).first()
            
            # 如果没有专门的拍卖保证金，检查通用保证金
            if not deposit:
                general_deposit = db.query(Deposit).filter(
                    and_(
                        Deposit.user_id == bidder_id,
                        Deposit.type == "general",
                        Deposit.status == "active"
                    )
                ).first()
                
                if not general_deposit:
                    raise ValueError("参与拍卖需要先缴纳保证金")
                
                # 检查通用保证金余额是否足够
                product = db.query(Product).filter(Product.id == product_id).first()
                required_deposit = product.current_price * self.AUCTION_RULES["deposit_rate"]
                
                if general_deposit.amount < required_deposit:
                    raise ValueError(f"保证金余额不足，需要至少{required_deposit}元")
            
        except Exception as e:
            if "保证金" in str(e):
                raise e
            logger.error(f"检查保证金失败: {e}")
            # 暂时允许继续出价，但记录错误
    
    async def normalize_auction_settings(self, db: Session, product_id: int) -> Dict[str, Any]:
        """标准化拍卖设置"""
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError("商品不存在")
        
        updates = {}
        normalized_count = 0
        
        # 标准化最小加价幅度
        if not product.min_bid_increment or product.min_bid_increment < self.AUCTION_RULES["min_bid_increment"]:
            updates["min_bid_increment"] = self.AUCTION_RULES["min_bid_increment"]
            normalized_count += 1
        
        # 标准化拍卖时长
        if product.auction_start_time and product.auction_end_time:
            duration = (product.auction_end_time - product.auction_start_time).total_seconds()
            
            if duration < self.AUCTION_RULES["min_auction_duration"]:
                new_end_time = product.auction_start_time + timedelta(
                    seconds=self.AUCTION_RULES["min_auction_duration"]
                )
                updates["auction_end_time"] = new_end_time
                normalized_count += 1
            
            elif duration > self.AUCTION_RULES["max_auction_duration"]:
                new_end_time = product.auction_start_time + timedelta(
                    seconds=self.AUCTION_RULES["max_auction_duration"]
                )
                updates["auction_end_time"] = new_end_time
                normalized_count += 1
        
        # 重置延时计数
        if product.extension_count and product.extension_count > 0:
            updates["extension_count"] = 0
            normalized_count += 1
        
        # 应用更新
        if updates:
            for key, value in updates.items():
                setattr(product, key, value)
            db.commit()
        
        return {
            "success": True,
            "normalized_count": normalized_count,
            "updates": updates,
            "message": f"已标准化 {normalized_count} 项设置"
        }