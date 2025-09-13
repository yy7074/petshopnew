from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from ..core.database import get_db
from ..core.security import get_current_user_optional
from ..models.user import User
from ..models.product import Product, Category, SpecialEvent
from ..schemas.product import ProductResponse
from ..schemas.home import HomeDataResponse, SpecialEventResponse, CategoryResponse

router = APIRouter()

@router.get("/", response_model=HomeDataResponse)
async def get_home_data(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取首页数据"""
    try:
        # 获取热门商品
        hot_products = db.query(Product).filter(
            Product.status == 2,  # 拍卖中
            Product.is_featured == True
        ).order_by(
            Product.view_count.desc(),
            Product.bid_count.desc()
        ).limit(10).all()
        
        # 获取最新商品
        recent_products = db.query(Product).filter(
            Product.status == 2  # 拍卖中
        ).order_by(
            Product.created_at.desc()
        ).limit(10).all()
        
        # 获取专场活动
        now = datetime.now()
        special_events = db.query(SpecialEvent).filter(
            SpecialEvent.is_active == True,
            SpecialEvent.start_time <= now,
            SpecialEvent.end_time >= now
        ).order_by(
            SpecialEvent.created_at.desc()
        ).limit(5).all()
        
        # 获取商品分类
        categories = db.query(Category).filter(
            Category.is_active == True
        ).order_by(
            Category.sort_order.asc(),
            Category.id.asc()
        ).limit(10).all()
        
        # 获取推荐商品（随机推荐）
        recommended_products = db.query(Product).filter(
            Product.status == 2
        ).order_by(func.random()).limit(5).all()
        
        # 转换为响应格式
        hot_products_data = [ProductResponse.from_orm(product) for product in hot_products]
        recent_products_data = [ProductResponse.from_orm(product) for product in recent_products]
        recommended_products_data = [ProductResponse.from_orm(product) for product in recommended_products]
        
        special_events_data = []
        for event in special_events:
            event_dict = {
                "id": event.id,
                "title": event.title,
                "description": event.description,
                "banner_image": event.banner_image,
                "start_time": event.start_time.isoformat() if event.start_time else None,
                "end_time": event.end_time.isoformat() if event.end_time else None,
                "is_active": event.is_active,
                "created_at": event.created_at.isoformat() if event.created_at else None,
            }
            special_events_data.append(event_dict)
        
        categories_data = [CategoryResponse.from_orm(category) for category in categories]
        
        return HomeDataResponse(
            hot_products=hot_products_data,
            recent_products=recent_products_data,
            recommended_products=recommended_products_data,
            special_events=special_events_data,
            categories=categories_data
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取首页数据失败: {str(e)}")

@router.get("/banners")
async def get_home_banners(
    db: Session = Depends(get_db)
):
    """获取首页轮播图"""
    try:
        # 这里可以从数据库获取轮播图配置
        # 暂时返回示例数据
        banners = [
            {
                "id": 1,
                "title": "宠物拍卖节",
                "image": "https://picsum.photos/800/400?random=1",
                "link": "/events/1",
                "sort_order": 1
            },
            {
                "id": 2,
                "title": "新品上架",
                "image": "https://picsum.photos/800/400?random=2",
                "link": "/products?sort=created_at&order=desc",
                "sort_order": 2
            },
            {
                "id": 3,
                "title": "热门推荐",
                "image": "https://picsum.photos/800/400?random=3",
                "link": "/products?featured=true",
                "sort_order": 3
            }
        ]
        
        return {
            "success": True,
            "data": banners
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取轮播图失败: {str(e)}")

@router.get("/stats")
async def get_home_stats(
    db: Session = Depends(get_db)
):
    """获取首页统计数据"""
    try:
        # 统计商品数量
        total_products = db.query(Product).filter(Product.status == 2).count()
        active_auctions = db.query(Product).filter(
            Product.status == 2,
            Product.auction_type == 1
        ).count()
        
        # 统计专场数量
        now = datetime.now()
        active_events = db.query(SpecialEvent).filter(
            SpecialEvent.is_active == True,
            SpecialEvent.start_time <= now,
            SpecialEvent.end_time >= now
        ).count()
        
        # 统计分类数量
        total_categories = db.query(Category).filter(Category.is_active == True).count()
        
        return {
            "success": True,
            "data": {
                "total_products": total_products,
                "active_auctions": active_auctions,
                "active_events": active_events,
                "total_categories": total_categories
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计数据失败: {str(e)}")
