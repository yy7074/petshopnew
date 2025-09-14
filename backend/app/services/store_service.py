from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal

from ..models.store import Store, StoreFollow, StoreReview
from ..models.product import Product
from ..models.user import User
from ..schemas.store import (
    StoreCreate, StoreUpdate, StoreResponse, StoreListResponse,
    StoreReviewCreate, StoreReviewResponse, StoreReviewListResponse,
    StoreStatsResponse
)

class StoreService:
    
    async def get_store_by_owner(self, db: Session, owner_id: int) -> Optional[StoreResponse]:
        """通过店主ID获取店铺"""
        store = db.query(Store).filter(Store.owner_id == owner_id).first()
        if not store:
            return None
        return self._to_store_response(store, db)
    
    async def get_store_by_id(self, db: Session, store_id: int, user_id: Optional[int] = None) -> Optional[StoreResponse]:
        """通过店铺ID获取店铺"""
        store = db.query(Store).filter(Store.id == store_id).first()
        if not store:
            return None
        return self._to_store_response(store, db, user_id)
    
    async def create_store(self, db: Session, store_data: StoreCreate, owner_id: int) -> StoreResponse:
        """创建店铺"""
        # 检查用户是否已有店铺
        existing_store = db.query(Store).filter(Store.owner_id == owner_id).first()
        if existing_store:
            raise ValueError("用户已经拥有店铺")
        
        # 创建店铺
        store = Store(
            owner_id=owner_id,
            name=store_data.name,
            description=store_data.description,
            avatar=store_data.avatar,
            banner=store_data.banner,
            location=store_data.location,
            phone=store_data.phone,
            is_open=store_data.is_open,
            business_hours=store_data.business_hours,
            announcement=store_data.announcement
        )
        
        db.add(store)
        db.commit()
        db.refresh(store)
        
        return self._to_store_response(store, db)
    
    async def update_store(self, db: Session, store_id: int, store_data: StoreUpdate, owner_id: int) -> StoreResponse:
        """更新店铺信息"""
        store = db.query(Store).filter(
            and_(Store.id == store_id, Store.owner_id == owner_id)
        ).first()
        
        if not store:
            raise ValueError("店铺不存在或无权限")
        
        # 更新字段
        for field, value in store_data.dict(exclude_unset=True).items():
            setattr(store, field, value)
        
        db.commit()
        db.refresh(store)
        
        return self._to_store_response(store, db)
    
    async def get_store_products(
        self, 
        db: Session, 
        store_id: int, 
        page: int = 1, 
        page_size: int = 20,
        category_id: Optional[int] = None,
        status: Optional[int] = None
    ) -> Dict[str, Any]:
        """获取店铺商品列表"""
        # 获取店铺信息
        store = db.query(Store).filter(Store.id == store_id).first()
        if not store:
            raise ValueError("店铺不存在")
        
        # 构建查询
        query = db.query(Product).filter(Product.seller_id == store.owner_id)
        
        if category_id:
            query = query.filter(Product.category_id == category_id)
        if status:
            query = query.filter(Product.status == status)
        else:
            query = query.filter(Product.status.in_([1, 2, 3]))  # 排除已删除的
        
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
                "images": product.images or [],
                "starting_price": str(product.starting_price),
                "current_price": str(product.current_price),
                "buy_now_price": str(product.buy_now_price) if product.buy_now_price else None,
                "auction_type": product.auction_type,
                "status": product.status,
                "view_count": product.view_count,
                "bid_count": product.bid_count,
                "favorite_count": product.favorite_count,
                "auction_end_time": product.auction_end_time.isoformat() if product.auction_end_time else None,
                "created_at": product.created_at.isoformat()
            }
            product_list.append(product_dict)
        
        return {
            "items": product_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
            "store_info": self._to_store_response(store, db)
        }
    
    async def follow_store(self, db: Session, store_id: int, user_id: int) -> bool:
        """关注店铺"""
        store = db.query(Store).filter(Store.id == store_id).first()
        if not store:
            raise ValueError("店铺不存在")
        
        # 检查是否已关注
        existing_follow = db.query(StoreFollow).filter(
            and_(StoreFollow.store_id == store_id, StoreFollow.user_id == user_id)
        ).first()
        
        if existing_follow:
            return False  # 已经关注
        
        # 创建关注记录
        follow = StoreFollow(store_id=store_id, user_id=user_id)
        db.add(follow)
        
        # 更新店铺关注数
        store.follower_count += 1
        
        db.commit()
        return True
    
    async def unfollow_store(self, db: Session, store_id: int, user_id: int) -> bool:
        """取消关注店铺"""
        store = db.query(Store).filter(Store.id == store_id).first()
        if not store:
            raise ValueError("店铺不存在")
        
        # 删除关注记录
        follow = db.query(StoreFollow).filter(
            and_(StoreFollow.store_id == store_id, StoreFollow.user_id == user_id)
        ).first()
        
        if not follow:
            return False  # 未关注
        
        db.delete(follow)
        
        # 更新店铺关注数
        if store.follower_count > 0:
            store.follower_count -= 1
        
        db.commit()
        return True
    
    async def get_store_reviews(
        self, 
        db: Session, 
        store_id: int, 
        page: int = 1, 
        page_size: int = 20,
        rating_filter: Optional[int] = None
    ) -> StoreReviewListResponse:
        """获取店铺评价列表"""
        query = db.query(StoreReview).filter(
            and_(StoreReview.store_id == store_id, StoreReview.status == 1)
        )
        
        if rating_filter:
            query = query.filter(StoreReview.rating == rating_filter)
        
        query = query.order_by(desc(StoreReview.created_at))
        
        # 分页
        total = query.count()
        offset = (page - 1) * page_size
        reviews = query.offset(offset).limit(page_size).all()
        
        # 获取评分统计
        rating_stats = db.query(
            StoreReview.rating,
            func.count(StoreReview.id).label('count')
        ).filter(
            and_(StoreReview.store_id == store_id, StoreReview.status == 1)
        ).group_by(StoreReview.rating).all()
        
        rating_summary = {f"{i}_star": 0 for i in range(1, 6)}
        total_ratings = 0
        total_score = 0
        
        for rating, count in rating_stats:
            rating_summary[f"{rating}_star"] = count
            total_ratings += count
            total_score += rating * count
        
        average_rating = total_score / total_ratings if total_ratings > 0 else 0.0
        
        # 转换评价数据
        review_list = []
        for review in reviews:
            user = db.query(User).filter(User.id == review.user_id).first()
            review_dict = {
                "id": review.id,
                "user_id": review.user_id,
                "store_id": review.store_id,
                "order_id": review.order_id,
                "rating": review.rating,
                "comment": review.comment,
                "images": review.images or [],
                "reply": review.reply,
                "replied_at": review.replied_at.isoformat() if review.replied_at else None,
                "status": review.status,
                "created_at": review.created_at.isoformat(),
                "updated_at": review.updated_at.isoformat(),
                "user_info": {
                    "nickname": user.nickname if user else "匿名用户",
                    "avatar": user.avatar if user else None
                }
            }
            review_list.append(review_dict)
        
        return StoreReviewListResponse(
            items=review_list,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size,
            rating_summary=rating_summary,
            average_rating=average_rating
        )
    
    async def get_store_stats(self, db: Session, store_id: int, owner_id: int) -> StoreStatsResponse:
        """获取店铺统计信息（仅店主可查看）"""
        store = db.query(Store).filter(
            and_(Store.id == store_id, Store.owner_id == owner_id)
        ).first()
        
        if not store:
            raise ValueError("店铺不存在或无权限")
        
        # 基础统计
        total_products = db.query(Product).filter(Product.seller_id == owner_id).count()
        active_products = db.query(Product).filter(
            and_(Product.seller_id == owner_id, Product.status == 2)
        ).count()
        
        # 评价统计
        total_reviews = db.query(StoreReview).filter(StoreReview.store_id == store_id).count()
        avg_rating = db.query(func.avg(StoreReview.rating)).filter(
            StoreReview.store_id == store_id
        ).scalar() or 0.0
        
        # 最近30天统计
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_reviews = db.query(StoreReview).filter(
            and_(
                StoreReview.store_id == store_id,
                StoreReview.created_at >= thirty_days_ago
            )
        ).count()
        
        return StoreStatsResponse(
            total_products=total_products,
            active_products=active_products,
            total_orders=store.total_sales,
            total_revenue=store.total_revenue,
            total_reviews=total_reviews,
            average_rating=float(avg_rating),
            follower_count=store.follower_count,
            recent_orders=0,  # 需要订单表支持
            recent_revenue=Decimal("0.00"),  # 需要订单表支持
            recent_reviews=recent_reviews
        )
    
    def _to_store_response(self, store: Store, db: Session, user_id: Optional[int] = None) -> StoreResponse:
        """转换为响应格式"""
        # 获取店主信息
        owner = db.query(User).filter(User.id == store.owner_id).first()
        
        # 检查是否关注
        is_following = False
        if user_id:
            follow = db.query(StoreFollow).filter(
                and_(StoreFollow.store_id == store.id, StoreFollow.user_id == user_id)
            ).first()
            is_following = bool(follow)
        
        # 获取最近商品
        recent_products_query = db.query(Product).filter(
            and_(Product.seller_id == store.owner_id, Product.status.in_([1, 2, 3]))
        ).order_by(desc(Product.created_at)).limit(6)
        
        recent_products = []
        for product in recent_products_query:
            product_dict = {
                "id": product.id,
                "title": product.title,
                "images": product.images or [],
                "current_price": str(product.current_price),
                "status": product.status
            }
            recent_products.append(product_dict)
        
        return StoreResponse(
            id=store.id,
            owner_id=store.owner_id,
            name=store.name,
            description=store.description,
            avatar=store.avatar,
            banner=store.banner,
            location=store.location,
            phone=store.phone,
            is_open=store.is_open,
            business_hours=store.business_hours,
            announcement=store.announcement,
            total_products=store.total_products,
            total_sales=store.total_sales,
            total_revenue=store.total_revenue,
            rating=store.rating,
            rating_count=store.rating_count,
            follower_count=store.follower_count,
            status=store.status,
            verified=store.verified,
            created_at=store.created_at,
            updated_at=store.updated_at,
            owner_info={
                "nickname": owner.nickname if owner else "店主",
                "avatar": owner.avatar_url if owner else None
            } if owner else None,
            is_following=is_following,
            recent_products=recent_products
        )