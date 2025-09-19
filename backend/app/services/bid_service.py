from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal

from ..models.product import Bid, AutoBid, Product
from ..models.user import User
from ..schemas.bid import BidCreate, BidResponse, BidListResponse, AutoBidCreate
from ..core.config import settings

class BidService:
    
    async def place_bid(
        self, 
        db: Session, 
        bid_data: BidCreate, 
        user_id: int
    ) -> BidResponse:
        """出价竞拍"""
        # 获取商品信息
        product = db.query(Product).filter(Product.id == bid_data.product_id).first()
        if not product:
            raise ValueError("商品不存在")
        
        # 允许用户对自己的商品出价（用于测试或特殊场景）
        # if product.seller_id == user_id:
        #     raise ValueError("不能对自己的商品出价")
        
        if product.status != 2:  # 2表示拍卖中
            raise ValueError("商品未在拍卖中")
        
        if product.auction_type == "fixed_price":
            raise ValueError("一口价商品无需竞拍")
        
        if product.auction_end_time and product.auction_end_time <= datetime.now():
            end_time_str = product.auction_end_time.strftime("%Y-%m-%d %H:%M:%S")
            raise ValueError(f"拍卖已于 {end_time_str} 结束，无法继续出价")
        
        # 检查出价金额
        if bid_data.amount <= product.current_price:
            raise ValueError(f"出价必须高于当前价格 ¥{product.current_price}")
        
        # 检查最小加价幅度
        min_increment = Decimal("1.00")  # 最小加价1元
        if bid_data.amount < product.current_price + min_increment:
            raise ValueError(f"最小加价幅度为 ¥{min_increment}")
        
        # 检查用户余额（如果需要）
        user = db.query(User).filter(User.id == user_id).first()
        if user.balance < bid_data.amount:
            raise ValueError("余额不足")
        
        # 创建出价记录
        bid = Bid(
            product_id=bid_data.product_id,
            bidder_id=user_id,
            bid_amount=bid_data.amount,
            is_auto_bid=False,
            status=1  # 1表示有效
        )
        db.add(bid)
        
        # 更新商品当前价格
        product.current_price = bid_data.amount
        
        # 将之前的出价状态改为outbid (2表示被超越)
        db.query(Bid).filter(
            and_(
                Bid.product_id == bid_data.product_id,
                Bid.id != bid.id,
                Bid.status == 1  # 1表示有效/领先
            )
        ).update({"status": 2})  # 2表示被超越
        
        # 设置当前出价为领先状态
        bid.status = 1  # 1表示有效/领先
        
        db.commit()
        db.refresh(bid)
        
        # 暂时注释掉自动出价处理
        # await self._handle_auto_bids(db, bid_data.product_id, bid_data.amount, user_id)
        
        return self._to_bid_response(bid, db)
    
    async def _handle_auto_bids(
        self, 
        db: Session, 
        product_id: int, 
        current_amount: Decimal, 
        exclude_user_id: int
    ):
        """处理自动出价"""
        # 获取该商品的活跃自动出价
        auto_bids = db.query(AutoBid).filter(
            and_(
                AutoBid.product_id == product_id,
                AutoBid.user_id != exclude_user_id,
                AutoBid.status == "active",
                AutoBid.max_amount > current_amount
            )
        ).order_by(desc(AutoBid.increment_amount)).all()
        
        for auto_bid in auto_bids:
            # 计算下一个出价金额
            next_amount = current_amount + auto_bid.increment_amount
            
            if next_amount <= auto_bid.max_amount:
                # 创建自动出价记录
                bid = Bid(
                    product_id=product_id,
                    bidder_id=auto_bid.user_id,
                    bid_amount=next_amount,
                    is_auto_bid=True,
                    status=1  # 1表示有效
                )
                db.add(bid)
                
                # 更新商品价格
                product = db.query(Product).filter(Product.id == product_id).first()
                product.current_price = next_amount
                
                # 更新之前的出价状态
                db.query(Bid).filter(
                    and_(
                        Bid.product_id == product_id,
                        Bid.id != bid.id,
                        Bid.status == "winning"
                    )
                ).update({"status": "outbid"})
                
                db.commit()
                current_amount = next_amount
                break
    
    async def get_product_bids(
        self, 
        db: Session, 
        product_id: int, 
        page: int = 1, 
        page_size: int = 20
    ) -> BidListResponse:
        """获取商品出价记录"""
        query = db.query(Bid).filter(Bid.product_id == product_id).order_by(desc(Bid.created_at))
        
        total = query.count()
        offset = (page - 1) * page_size
        bids = query.offset(offset).limit(page_size).all()
        
        return BidListResponse(
            items=[self._to_bid_response(bid, db) for bid in bids],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )
    
    async def get_user_bids(
        self, 
        db: Session, 
        user_id: int, 
        page: int = 1, 
        page_size: int = 20,
        status: Optional[str] = None
    ) -> BidListResponse:
        """获取用户出价记录"""
        query = db.query(Bid).filter(Bid.bidder_id == user_id)
        
        if status:
            query = query.filter(Bid.status == status)
        
        query = query.order_by(desc(Bid.created_at))
        
        total = query.count()
        offset = (page - 1) * page_size
        bids = query.offset(offset).limit(page_size).all()
        
        return BidListResponse(
            items=[self._to_bid_response(bid, db) for bid in bids],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )
    
    async def get_winning_bids(
        self, 
        db: Session, 
        user_id: int, 
        page: int = 1, 
        page_size: int = 20
    ) -> BidListResponse:
        """获取用户正在领先的竞拍"""
        query = db.query(Bid).filter(
            and_(
                Bid.bidder_id == user_id,
                Bid.status == "winning"
            )
        ).order_by(desc(Bid.created_at))
        
        total = query.count()
        offset = (page - 1) * page_size
        bids = query.offset(offset).limit(page_size).all()
        
        return BidListResponse(
            items=[self._to_bid_response(bid, db) for bid in bids],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )
    
    async def get_bid_history(
        self, 
        db: Session, 
        user_id: int, 
        page: int = 1, 
        page_size: int = 20,
        product_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> BidListResponse:
        """获取竞拍历史"""
        query = db.query(Bid).filter(Bid.bidder_id == user_id)
        
        if product_id:
            query = query.filter(Bid.product_id == product_id)
        
        if start_date:
            query = query.filter(Bid.created_at >= datetime.fromisoformat(start_date))
        
        if end_date:
            query = query.filter(Bid.created_at <= datetime.fromisoformat(end_date))
        
        query = query.order_by(desc(Bid.created_at))
        
        total = query.count()
        offset = (page - 1) * page_size
        bids = query.offset(offset).limit(page_size).all()
        
        return BidListResponse(
            items=[self._to_bid_response(bid, db) for bid in bids],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )
    
    async def create_auto_bid(
        self, 
        db: Session, 
        auto_bid_data: AutoBidCreate, 
        user_id: int
    ) -> AutoBid:
        """创建自动出价"""
        # 验证商品
        product = db.query(Product).filter(Product.id == auto_bid_data.product_id).first()
        if not product:
            raise ValueError("商品不存在")
        
        if product.seller_id == user_id:
            raise ValueError("不能对自己的商品设置自动出价")
        
        # 检查是否已有自动出价
        existing = db.query(AutoBid).filter(
            and_(
                AutoBid.product_id == auto_bid_data.product_id,
                AutoBid.user_id == user_id,
                AutoBid.status == "active"
            )
        ).first()
        
        if existing:
            raise ValueError("该商品已设置自动出价")
        
        # 创建自动出价
        auto_bid = AutoBid(
            product_id=auto_bid_data.product_id,
            user_id=user_id,
            max_amount=auto_bid_data.max_amount,
            increment_amount=auto_bid_data.increment_amount,
            status="active"
        )
        
        db.add(auto_bid)
        db.commit()
        db.refresh(auto_bid)
        
        return auto_bid
    
    async def get_user_auto_bids(
        self, 
        db: Session, 
        user_id: int, 
        page: int = 1, 
        page_size: int = 20,
        status: str = "active"
    ):
        """获取用户自动出价设置"""
        query = db.query(AutoBid).filter(
            and_(
                AutoBid.user_id == user_id,
                AutoBid.status == status
            )
        ).order_by(desc(AutoBid.created_at))
        
        total = query.count()
        offset = (page - 1) * page_size
        auto_bids = query.offset(offset).limit(page_size).all()
        
        items = []
        for auto_bid in auto_bids:
            product = db.query(Product).filter(Product.id == auto_bid.product_id).first()
            items.append({
                "id": auto_bid.id,
                "product_id": auto_bid.product_id,
                "product_title": product.title if product else None,
                "max_amount": auto_bid.max_amount,
                "increment_amount": auto_bid.increment_amount,
                "status": auto_bid.status,
                "created_at": auto_bid.created_at
            })
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    
    async def pause_auto_bid(self, db: Session, auto_bid_id: int, user_id: int) -> bool:
        """暂停自动出价"""
        auto_bid = db.query(AutoBid).filter(
            and_(AutoBid.id == auto_bid_id, AutoBid.user_id == user_id)
        ).first()
        
        if not auto_bid:
            return False
        
        auto_bid.status = "paused"
        db.commit()
        return True
    
    async def resume_auto_bid(self, db: Session, auto_bid_id: int, user_id: int) -> bool:
        """恢复自动出价"""
        auto_bid = db.query(AutoBid).filter(
            and_(AutoBid.id == auto_bid_id, AutoBid.user_id == user_id)
        ).first()
        
        if not auto_bid:
            return False
        
        auto_bid.status = "active"
        db.commit()
        return True
    
    async def cancel_auto_bid(self, db: Session, auto_bid_id: int, user_id: int) -> bool:
        """取消自动出价"""
        auto_bid = db.query(AutoBid).filter(
            and_(AutoBid.id == auto_bid_id, AutoBid.user_id == user_id)
        ).first()
        
        if not auto_bid:
            return False
        
        auto_bid.status = "cancelled"
        db.commit()
        return True
    
    async def get_user_bid_statistics(self, db: Session, user_id: int) -> Dict[str, Any]:
        """获取用户出价统计"""
        # 总出价次数
        total_bids = db.query(func.count(Bid.id)).filter(Bid.bidder_id == user_id).scalar()
        
        # 赢得的拍卖数
        won_auctions = db.query(func.count(Bid.id)).filter(
            and_(Bid.bidder_id == user_id, Bid.status == 2)  # 2表示获胜
        ).scalar()
        
        # 正在领先的拍卖数
        winning_auctions = db.query(func.count(Bid.id)).filter(
            and_(Bid.bidder_id == user_id, Bid.status == 1)  # 1表示有效/领先
        ).scalar()
        
        # 总出价金额
        total_amount = db.query(func.sum(Bid.bid_amount)).filter(Bid.bidder_id == user_id).scalar() or 0
        
        # 平均出价
        avg_amount = total_amount / total_bids if total_bids > 0 else 0
        
        return {
            "total_bids": total_bids,
            "won_auctions": won_auctions,
            "winning_auctions": winning_auctions,
            "total_amount": float(total_amount),
            "average_amount": float(avg_amount),
            "success_rate": won_auctions / total_bids if total_bids > 0 else 0
        }
    
    async def get_bid_detail(
        self, 
        db: Session, 
        bid_id: int, 
        user_id: int
    ) -> Optional[BidResponse]:
        """获取出价详情"""
        bid = db.query(Bid).filter(
            and_(Bid.id == bid_id, Bid.bidder_id == user_id)
        ).first()
        
        if not bid:
            return None
        
        return self._to_bid_response(bid, db)
    
    async def cancel_bid(self, db: Session, bid_id: int, user_id: int) -> bool:
        """取消出价（仅在特定条件下允许）"""
        bid = db.query(Bid).filter(
            and_(Bid.id == bid_id, Bid.bidder_id == user_id)
        ).first()
        
        if not bid:
            return False
        
        # 只有在非领先状态下才能取消
        if bid.status == "winning":
            raise ValueError("领先出价不能取消")
        
        if bid.status in ["won", "lost", "cancelled"]:
            raise ValueError("该出价已结束，不能取消")
        
        bid.status = "cancelled"
        db.commit()
        return True
    
    def _to_bid_response(self, bid: Bid, db: Session) -> BidResponse:
        """转换为响应格式"""
        # 获取用户信息
        user = db.query(User).filter(User.id == bid.bidder_id).first()
        
        # 获取商品信息
        product = db.query(Product).filter(Product.id == bid.product_id).first()
        
        return BidResponse(
            id=bid.id,
            product_id=bid.product_id,
            user_id=bid.bidder_id,
            amount=bid.bid_amount,
            is_auto_bid=bid.is_auto_bid,
            status=bid.status,
            created_at=bid.created_at,
            user_info={
                "username": user.username,
                "avatar": user.avatar_url
            } if user else None,
            product_info={
                "title": product.title,
                "image": product.images[0] if product.images else None
            } if product else None
        )