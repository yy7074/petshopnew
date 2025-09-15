from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal

from ..models.product import Product
from ..models.order import Order
from ..models.store import Store
from ..models.user import User
from ..schemas.product import ProductListResponse

class SellerService:
    
    async def get_seller_dashboard(self, db: Session, seller_id: int) -> Dict[str, Any]:
        """获取卖家仪表盘数据"""
        # 基础统计
        total_products = db.query(Product).filter(Product.seller_id == seller_id).count()
        active_products = db.query(Product).filter(
            and_(Product.seller_id == seller_id, Product.status == 2)
        ).count()
        
        # 获取店铺信息
        store = db.query(Store).filter(Store.owner_id == seller_id).first()
        
        # 最近7天统计
        seven_days_ago = datetime.now() - timedelta(days=7)
        recent_products = db.query(Product).filter(
            and_(
                Product.seller_id == seller_id,
                Product.created_at >= seven_days_ago
            )
        ).count()
        
        # 待处理订单数量（假设status=1是待处理）
        pending_orders = 0  # 需要订单表支持
        
        return {
            "store_info": {
                "id": store.id if store else None,
                "name": store.name if store else "未开店",
                "is_open": store.is_open if store else False,
                "verified": store.verified if store else False,
                "follower_count": store.follower_count if store else 0,
                "rating": float(store.rating) if store else 0.0
            },
            "product_stats": {
                "total_products": total_products,
                "active_products": active_products,
                "recent_products": recent_products,
                "draft_products": db.query(Product).filter(
                    and_(Product.seller_id == seller_id, Product.status == 1)
                ).count()
            },
            "order_stats": {
                "pending_orders": pending_orders,
                "total_sales": store.total_sales if store else 0,
                "total_revenue": float(store.total_revenue) if store else 0.0
            },
            "recent_activities": await self._get_recent_activities(db, seller_id)
        }
    
    async def get_seller_products(
        self, 
        db: Session, 
        seller_id: int, 
        page: int = 1, 
        page_size: int = 20,
        status: Optional[int] = None,
        category_id: Optional[int] = None,
        keyword: Optional[str] = None
    ) -> ProductListResponse:
        """获取卖家商品列表"""
        query = db.query(Product).filter(Product.seller_id == seller_id)
        
        if status is not None:
            query = query.filter(Product.status == status)
        else:
            query = query.filter(Product.status != 5)  # 排除已删除
        
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        if keyword:
            query = query.filter(
                or_(
                    Product.title.contains(keyword),
                    Product.description.contains(keyword)
                )
            )
        
        query = query.order_by(desc(Product.created_at))
        
        # 分页
        total = query.count()
        offset = (page - 1) * page_size
        products = query.offset(offset).limit(page_size).all()
        
        # 转换为字典格式
        product_list = []
        for product in products:
            product_dict = {
                "id": product.id,
                "title": product.title,
                "description": product.description,
                "images": product.images or [],
                "starting_price": str(product.starting_price),
                "current_price": str(product.current_price),
                "buy_now_price": str(product.buy_now_price) if product.buy_now_price else None,
                "auction_type": product.auction_type,
                "status": product.status,
                "category_id": product.category_id,
                "view_count": product.view_count,
                "bid_count": product.bid_count,
                "favorite_count": product.favorite_count,
                "auction_end_time": product.auction_end_time.isoformat() if product.auction_end_time else None,
                "created_at": product.created_at.isoformat(),
                "updated_at": product.updated_at.isoformat()
            }
            product_list.append(product_dict)
        
        return ProductListResponse(
            items=product_list,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )
    
    async def toggle_product_status(self, db: Session, product_id: int, seller_id: int) -> Dict[str, Any]:
        """切换商品上下架状态"""
        product = db.query(Product).filter(
            and_(Product.id == product_id, Product.seller_id == seller_id)
        ).first()
        
        if not product:
            raise ValueError("商品不存在或无权限")
        
        # 切换状态：1(草稿) <-> 2(上架)
        if product.status == 1:
            product.status = 2  # 上架
            message = "商品已上架"
        elif product.status == 2:
            product.status = 1  # 下架到草稿
            message = "商品已下架"
        else:
            raise ValueError("商品状态不允许切换")
        
        db.commit()
        
        return {
            "product_id": product_id,
            "status": product.status,
            "message": message
        }
    
    async def delete_product(self, db: Session, product_id: int, seller_id: int) -> Dict[str, Any]:
        """删除商品（软删除）"""
        product = db.query(Product).filter(
            and_(Product.id == product_id, Product.seller_id == seller_id)
        ).first()
        
        if not product:
            raise ValueError("商品不存在或无权限")
        
        if product.status == 3:  # 拍卖中不能删除
            raise ValueError("拍卖中的商品不能删除")
        
        # 软删除
        product.status = 5  # 已删除
        db.commit()
        
        return {
            "product_id": product_id,
            "message": "商品已删除"
        }
    
    async def get_seller_orders(
        self, 
        db: Session, 
        seller_id: int, 
        page: int = 1, 
        page_size: int = 20,
        status: Optional[int] = None
    ) -> Dict[str, Any]:
        """获取卖家订单列表"""
        # 这里需要根据实际的订单表结构来实现
        # 目前返回空列表作为占位符
        return {
            "items": [],
            "total": 0,
            "page": page,
            "page_size": page_size,
            "total_pages": 0,
            "message": "订单功能开发中"
        }
    
    async def ship_order(self, db: Session, order_id: int, tracking_number: str, seller_id: int) -> Dict[str, Any]:
        """发货"""
        # 这里需要根据实际的订单表结构来实现
        return {
            "order_id": order_id,
            "tracking_number": tracking_number,
            "message": "发货功能开发中"
        }
    
    async def get_seller_statistics(self, db: Session, seller_id: int, days: int = 30) -> Dict[str, Any]:
        """获取卖家统计数据"""
        start_date = datetime.now() - timedelta(days=days)
        
        # 商品统计
        products_query = db.query(Product).filter(Product.seller_id == seller_id)
        total_products = products_query.count()
        recent_products = products_query.filter(Product.created_at >= start_date).count()
        
        # 浏览量统计
        total_views = db.query(func.sum(Product.view_count)).filter(
            Product.seller_id == seller_id
        ).scalar() or 0
        
        # 收藏统计
        total_favorites = db.query(func.sum(Product.favorite_count)).filter(
            Product.seller_id == seller_id
        ).scalar() or 0
        
        # 按日期分组的统计（最近30天）
        daily_stats = []
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            date_end = date_start + timedelta(days=1)
            
            daily_products = db.query(Product).filter(
                and_(
                    Product.seller_id == seller_id,
                    Product.created_at >= date_start,
                    Product.created_at < date_end
                )
            ).count()
            
            daily_stats.append({
                "date": date_start.strftime("%Y-%m-%d"),
                "products": daily_products,
                "views": 0,  # 需要访问日志支持
                "orders": 0   # 需要订单表支持
            })
        
        return {
            "period_days": days,
            "overview": {
                "total_products": total_products,
                "recent_products": recent_products,
                "total_views": total_views,
                "total_favorites": total_favorites,
                "total_orders": 0,  # 需要订单表支持
                "total_revenue": 0.0  # 需要订单表支持
            },
            "daily_stats": list(reversed(daily_stats))  # 最新日期在前
        }
    
    async def _get_recent_activities(self, db: Session, seller_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最近活动"""
        activities = []
        
        # 最近发布的商品
        recent_products = db.query(Product).filter(
            Product.seller_id == seller_id
        ).order_by(desc(Product.created_at)).limit(limit).all()
        
        for product in recent_products:
            activities.append({
                "type": "product_created",
                "title": f"发布了商品《{product.title}》",
                "time": product.created_at.isoformat(),
                "data": {
                    "product_id": product.id,
                    "product_title": product.title
                }
            })
        
        # 按时间排序
        activities.sort(key=lambda x: x["time"], reverse=True)
        
        return activities[:limit]
