from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..schemas.product import ProductResponse, ProductListResponse
from ..services.seller_service import SellerService

router = APIRouter()
seller_service = SellerService()

@router.get("/dashboard")
async def get_seller_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取卖家仪表盘数据"""
    try:
        dashboard_data = await seller_service.get_seller_dashboard(db, current_user.id)
        return dashboard_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/products", response_model=ProductListResponse)
async def get_seller_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[int] = None,
    category_id: Optional[int] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取卖家商品列表"""
    try:
        products = await seller_service.get_seller_products(
            db, current_user.id, page, page_size, status, category_id, keyword
        )
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/products/{product_id}/toggle-status")
async def toggle_product_status(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """切换商品上下架状态"""
    try:
        if product_id <= 0:
            raise HTTPException(status_code=400, detail="无效的商品ID")
            
        result = await seller_service.toggle_product_status(db, product_id, current_user.id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/products/{product_id}")
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除商品"""
    try:
        if product_id <= 0:
            raise HTTPException(status_code=400, detail="无效的商品ID")
            
        result = await seller_service.delete_product(db, product_id, current_user.id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orders")
async def get_seller_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取卖家订单列表"""
    try:
        orders = await seller_service.get_seller_orders(
            db, current_user.id, page, page_size, status
        )
        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/orders/{order_id}/ship")
async def ship_order(
    order_id: int,
    tracking_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """发货"""
    try:
        if order_id <= 0:
            raise HTTPException(status_code=400, detail="无效的订单ID")
        if not tracking_number.strip():
            raise HTTPException(status_code=400, detail="快递单号不能为空")
            
        result = await seller_service.ship_order(db, order_id, tracking_number, current_user.id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics")
async def get_seller_statistics(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取卖家统计数据"""
    try:
        stats = await seller_service.get_seller_statistics(db, current_user.id, days)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
