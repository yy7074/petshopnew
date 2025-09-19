from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal

from ..models.store import Store
from ..models.store_application import StoreApplication
from ..models.product import Product, Bid, Category
from ..models.order import Order
from ..models.user import User
from ..schemas.product import ProductCreate
from .store_application_service import StoreApplicationService
from .auction_service import AuctionService

class SellerCenterService:
    """商家中心服务"""
    
    def __init__(self):
        self.store_application_service = StoreApplicationService()
        self.auction_service = AuctionService()
    
    async def get_seller_dashboard(self, db: Session, user_id: int) -> Dict[str, Any]:
        """获取商家仪表板数据"""
        
        # 检查商家状态
        store = db.query(Store).filter(Store.owner_id == user_id).first()
        store_application = db.query(StoreApplication).filter(
            StoreApplication.user_id == user_id
        ).order_by(desc(StoreApplication.created_at)).first()
        
        if not store and not store_application:
            return {
                "seller_status": "not_applied",
                "message": "尚未申请开店",
                "next_step": "apply_store"
            }
        
        if not store and store_application:
            return {
                "seller_status": "application_pending",
                "application_status": store_application.status,
                "message": self._get_application_status_message(store_application.status),
                "application_id": store_application.id
            }
        
        # 商家已开店，获取统计数据
        stats = await self._get_seller_stats(db, user_id, store.id)
        
        return {
            "seller_status": "active",
            "store_info": {
                "id": store.id,
                "name": store.shop_name,
                "rating": float(store.rating),
                "total_sales": store.total_sales,
                "status": store.status
            },
            "stats": stats
        }
    
    def _get_application_status_message(self, status: int) -> str:
        """获取申请状态消息"""
        status_messages = {
            0: "申请已提交，等待审核",
            1: "申请已通过，请完成支付开店",
            2: "申请被拒绝，请查看拒绝原因",
            3: "店铺已开通"
        }
        return status_messages.get(status, "未知状态")
    
    async def _get_seller_stats(self, db: Session, user_id: int, store_id: int) -> Dict[str, Any]:
        """获取商家统计数据"""
        
        # 商品统计
        product_stats = db.query(
            func.count(Product.id).label('total'),
            func.sum(func.case([(Product.status == 2, 1)], else_=0)).label('active_auctions'),
            func.sum(func.case([(Product.status == 3, 1)], else_=0)).label('ended_auctions'),
            func.sum(Product.view_count).label('total_views')
        ).filter(Product.seller_id == user_id).first()
        
        # 订单统计（最近30天）
        thirty_days_ago = datetime.now() - timedelta(days=30)
        order_stats = db.query(
            func.count(Order.id).label('total_orders'),
            func.sum(Order.total_amount).label('total_amount'),
            func.sum(func.case([(Order.order_status == 6, 1)], else_=0)).label('completed_orders')
        ).filter(
            and_(
                Order.seller_id == user_id,
                Order.created_at >= thirty_days_ago
            )
        ).first()
        
        # 出价统计
        bid_stats = db.query(
            func.count(Bid.id).label('total_bids')
        ).join(Product).filter(Product.seller_id == user_id).first()
        
        return {
            "products": {
                "total": product_stats.total or 0,
                "active_auctions": product_stats.active_auctions or 0,
                "ended_auctions": product_stats.ended_auctions or 0,
                "total_views": product_stats.total_views or 0
            },
            "orders": {
                "total_orders": order_stats.total_orders or 0,
                "total_amount": float(order_stats.total_amount or 0),
                "completed_orders": order_stats.completed_orders or 0
            },
            "engagement": {
                "total_bids": bid_stats.total_bids or 0
            }
        }
    
    async def create_seller_product(
        self, 
        db: Session, 
        product_data: ProductCreate, 
        seller_id: int
    ) -> Dict[str, Any]:
        """商家创建产品（带验证）"""
        
        # 验证商家状态
        store = db.query(Store).filter(Store.owner_id == seller_id).first()
        if not store:
            raise ValueError("您还没有开店，请先申请开店")
        
        if store.status != 1:
            raise ValueError("店铺状态异常，无法发布商品")
        
        # 如果是拍卖商品，验证拍卖设置
        if product_data.auction_type in [1, 3]:  # 拍卖或混合
            auction_validation = await self.auction_service.validate_auction_setup(
                db, product_data.dict()
            )
            if not auction_validation["is_valid"]:
                raise ValueError(f"拍卖设置不符合规范: {', '.join(auction_validation['errors'])}")
            
            # 使用标准化的拍卖数据
            normalized_data = auction_validation["normalized_data"]
            for key, value in normalized_data.items():
                if hasattr(product_data, key):
                    setattr(product_data, key, value)
        
        # 创建商品
        product = Product(
            seller_id=seller_id,
            category_id=product_data.category_id,
            title=product_data.title,
            description=product_data.description,
            images=product_data.images or [],
            starting_price=product_data.starting_price,
            current_price=product_data.starting_price,
            buy_now_price=product_data.buy_now_price,
            auction_type=product_data.auction_type,
            auction_start_time=product_data.auction_start_time,
            auction_end_time=product_data.auction_end_time,
            location=product_data.location,
            shipping_fee=product_data.shipping_fee or Decimal("0.00"),
            is_free_shipping=product_data.is_free_shipping or False,
            condition_type=product_data.condition_type or 1,
            stock_quantity=product_data.stock_quantity or 1,
            status=1,  # 待审核
            min_bid_increment=getattr(product_data, 'min_bid_increment', Decimal("1.00"))
        )
        
        db.add(product)
        db.commit()
        db.refresh(product)
        
        return {
            "product_id": product.id,
            "title": product.title,
            "status": product.status,
            "message": "商品创建成功，等待审核"
        }
    
    async def get_seller_products(
        self, 
        db: Session, 
        seller_id: int,
        page: int = 1,
        page_size: int = 20,
        status: Optional[int] = None
    ) -> Dict[str, Any]:
        """获取商家商品列表"""
        
        query = db.query(Product).filter(Product.seller_id == seller_id)
        
        if status is not None:
            query = query.filter(Product.status == status)
        
        total = query.count()
        products = query.order_by(desc(Product.created_at)).offset(
            (page - 1) * page_size
        ).limit(page_size).all()
        
        product_list = []
        for product in products:
            # 获取最新出价信息
            latest_bid = db.query(Bid).filter(
                Bid.product_id == product.id
            ).order_by(desc(Bid.created_at)).first()
            
            product_list.append({
                "id": product.id,
                "title": product.title,
                "images": product.images,
                "starting_price": float(product.starting_price),
                "current_price": float(product.current_price),
                "auction_type": product.auction_type,
                "status": product.status,
                "view_count": product.view_count,
                "bid_count": product.bid_count,
                "auction_start_time": product.auction_start_time.isoformat() if product.auction_start_time else None,
                "auction_end_time": product.auction_end_time.isoformat() if product.auction_end_time else None,
                "latest_bid": {
                    "amount": float(latest_bid.bid_amount) if latest_bid else None,
                    "time": latest_bid.created_at.isoformat() if latest_bid else None
                },
                "created_at": product.created_at.isoformat()
            })
        
        return {
            "items": product_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    
    async def update_product_status(
        self, 
        db: Session, 
        product_id: int, 
        seller_id: int, 
        new_status: int
    ) -> Dict[str, Any]:
        """更新商品状态"""
        
        product = db.query(Product).filter(
            and_(
                Product.id == product_id,
                Product.seller_id == seller_id
            )
        ).first()
        
        if not product:
            raise ValueError("商品不存在或无权限操作")
        
        # 状态变更规则验证
        if product.status == 2 and new_status == 4:  # 拍卖中 -> 下架
            # 检查是否有活跃出价
            active_bids = db.query(Bid).filter(
                and_(
                    Bid.product_id == product_id,
                    Bid.status == 1
                )
            ).count()
            
            if active_bids > 0:
                raise ValueError("拍卖进行中，有活跃出价，无法下架")
        
        old_status = product.status
        product.status = new_status
        product.updated_at = datetime.now()
        
        db.commit()
        
        status_names = {1: "待审核", 2: "拍卖中", 3: "已结束", 4: "已下架"}
        
        return {
            "product_id": product_id,
            "old_status": old_status,
            "new_status": new_status,
            "message": f"商品状态已更新为: {status_names.get(new_status, '未知')}"
        }
    
    async def get_seller_orders(
        self, 
        db: Session, 
        seller_id: int,
        page: int = 1,
        page_size: int = 20,
        status: Optional[int] = None
    ) -> Dict[str, Any]:
        """获取商家订单列表"""
        
        query = db.query(Order).filter(Order.seller_id == seller_id)
        
        if status is not None:
            query = query.filter(Order.order_status == status)
        
        total = query.count()
        orders = query.order_by(desc(Order.created_at)).offset(
            (page - 1) * page_size
        ).limit(page_size).all()
        
        order_list = []
        for order in orders:
            # 获取买家信息
            buyer = db.query(User).filter(User.id == order.buyer_id).first()
            # 获取商品信息
            product = db.query(Product).filter(Product.id == order.product_id).first()
            
            order_list.append({
                "id": order.id,
                "order_no": order.order_no,
                "buyer": {
                    "id": buyer.id if buyer else None,
                    "username": buyer.username if buyer else "未知用户"
                },
                "product": {
                    "id": product.id if product else None,
                    "title": product.title if product else "商品已删除",
                    "images": product.images[0] if product and product.images else None
                },
                "total_amount": float(order.total_amount),
                "payment_status": order.payment_status,
                "order_status": order.order_status,
                "created_at": order.created_at.isoformat(),
                "shipping_address": order.shipping_address
            })
        
        return {
            "items": order_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    
    async def get_store_rating_summary(self, db: Session, store_id: int) -> Dict[str, Any]:
        """获取店铺评价汇总"""
        
        # 这里可以扩展评价系统
        # 暂时返回基础店铺信息
        store = db.query(Store).filter(Store.id == store_id).first()
        if not store:
            raise ValueError("店铺不存在")
        
        return {
            "store_id": store_id,
            "rating": float(store.rating),
            "total_sales": store.total_sales,
            "rating_breakdown": {
                "5_star": 0,
                "4_star": 0,
                "3_star": 0,
                "2_star": 0,
                "1_star": 0
            },
            "recent_reviews": []
        }