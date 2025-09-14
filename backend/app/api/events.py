from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..core.database import get_db
from ..models.product import SpecialEvent, EventProduct, Product

router = APIRouter()

@router.get("/")
async def get_special_events(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = Query(True),
    db: Session = Depends(get_db)
):
    """获取专场活动列表"""
    try:
        query = db.query(SpecialEvent)
        
        if is_active is not None:
            query = query.filter(SpecialEvent.is_active == is_active)
            
        # 只显示进行中的活动
        if is_active:
            now = datetime.now()
            query = query.filter(
                SpecialEvent.start_time <= now,
                SpecialEvent.end_time >= now
            )
        
        total = query.count()
        events = query.order_by(SpecialEvent.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        
        # 转换为响应格式
        event_list = []
        for event in events:
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
            event_list.append(event_dict)
        
        return {
            "items": event_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="获取专场活动失败")

@router.get("/{event_id}")
async def get_special_event(
    event_id: int,
    db: Session = Depends(get_db)
):
    """获取专场活动详情"""
    try:
        event = db.query(SpecialEvent).filter(SpecialEvent.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="专场活动不存在")
        
        return {
            "id": event.id,
            "title": event.title,
            "description": event.description,
            "banner_image": event.banner_image,
            "start_time": event.start_time.isoformat() if event.start_time else None,
            "end_time": event.end_time.isoformat() if event.end_time else None,
            "is_active": event.is_active,
            "created_at": event.created_at.isoformat() if event.created_at else None,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="获取专场活动详情失败")

@router.get("/{event_id}/products")
async def get_event_products(
    event_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取专场活动中的商品"""
    try:
        # 验证专场活动是否存在
        event = db.query(SpecialEvent).filter(SpecialEvent.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="专场活动不存在")
        
        # 查询专场中的商品
        query = db.query(Product).join(
            EventProduct, Product.id == EventProduct.product_id
        ).filter(EventProduct.event_id == event_id)
        
        total = query.count()
        products = query.order_by(EventProduct.sort_order, Product.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        
        # 转换为响应格式
        product_list = []
        for product in products:
            product_dict = {
                "id": product.id,
                "seller_id": product.seller_id,  # 添加缺失的seller_id字段
                "title": product.title,
                "description": product.description,
                "category_id": product.category_id,  # 添加缺失的category_id字段
                "images": product.images or [],
                "starting_price": str(product.starting_price) if product.starting_price else "0",
                "current_price": str(product.current_price) if product.current_price else "0", 
                "buy_now_price": str(product.buy_now_price) if product.buy_now_price else None,
                "auction_type": product.auction_type,
                "auction_start_time": product.auction_start_time.isoformat() if product.auction_start_time else None,
                "auction_end_time": product.auction_end_time.isoformat() if product.auction_end_time else None,
                "location": product.location,
                "shipping_fee": str(product.shipping_fee) if product.shipping_fee else "0",
                "is_free_shipping": product.is_free_shipping,
                "condition_type": product.condition_type,
                "stock_quantity": product.stock_quantity,
                "view_count": product.view_count,
                "bid_count": product.bid_count,
                "favorite_count": product.favorite_count,
                "status": product.status,
                "is_featured": product.is_featured,
                "created_at": product.created_at.isoformat() if product.created_at else None,
                "updated_at": product.updated_at.isoformat() if product.updated_at else None,  # 添加updated_at字段
            }
            product_list.append(product_dict)
        
        return {
            "items": product_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
            "event": {
                "id": event.id,
                "title": event.title,
                "description": event.description,
                "banner_image": event.banner_image,
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="获取专场商品失败")