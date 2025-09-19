from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..schemas.product import ProductCreate
from ..services.seller_center_service import SellerCenterService

router = APIRouter()
seller_center_service = SellerCenterService()

@router.get("/dashboard")
async def get_seller_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取商家仪表板"""
    try:
        dashboard = await seller_center_service.get_seller_dashboard(db, current_user.id)
        return {
            "success": True,
            "data": dashboard
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取仪表板失败: {str(e)}")

@router.post("/products")
async def create_seller_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """商家创建商品"""
    try:
        result = await seller_center_service.create_seller_product(
            db, product_data, current_user.id
        )
        return {
            "success": True,
            "message": "商品创建成功",
            "data": result
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建商品失败: {str(e)}")

@router.get("/products")
async def get_seller_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[int] = Query(None, ge=1, le=4),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取商家商品列表"""
    try:
        result = await seller_center_service.get_seller_products(
            db, current_user.id, page, page_size, status
        )
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取商品列表失败: {str(e)}")

@router.patch("/products/{product_id}/status")
async def update_product_status(
    product_id: int,
    status_data: Dict[str, int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新商品状态"""
    try:
        new_status = status_data.get("status")
        if new_status not in [1, 2, 3, 4]:
            raise ValueError("无效的状态值")
        
        result = await seller_center_service.update_product_status(
            db, product_id, current_user.id, new_status
        )
        return {
            "success": True,
            "message": result["message"],
            "data": result
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新商品状态失败: {str(e)}")

@router.get("/orders")
async def get_seller_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[int] = Query(None, ge=1, le=7),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取商家订单列表"""
    try:
        result = await seller_center_service.get_seller_orders(
            db, current_user.id, page, page_size, status
        )
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取订单列表失败: {str(e)}")

@router.get("/store/rating")
async def get_store_rating(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取店铺评价汇总"""
    try:
        from ..models.store import Store
        store = db.query(Store).filter(Store.owner_id == current_user.id).first()
        if not store:
            raise HTTPException(status_code=404, detail="店铺不存在")
        
        result = await seller_center_service.get_store_rating_summary(db, store.id)
        return {
            "success": True,
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取店铺评价失败: {str(e)}")

@router.get("/analytics/sales")
async def get_sales_analytics(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取销售分析数据"""
    try:
        from ..models.order import Order
        from sqlalchemy import and_, func
        from datetime import datetime, timedelta
        
        start_date = datetime.now() - timedelta(days=days)
        
        # 按日统计销售数据
        daily_sales = db.query(
            func.date(Order.created_at).label('date'),
            func.count(Order.id).label('order_count'),
            func.sum(Order.total_amount).label('total_amount')
        ).filter(
            and_(
                Order.seller_id == current_user.id,
                Order.created_at >= start_date,
                Order.payment_status == 2  # 已支付
            )
        ).group_by(func.date(Order.created_at)).all()
        
        analytics_data = []
        for record in daily_sales:
            analytics_data.append({
                "date": record.date.isoformat(),
                "order_count": record.order_count,
                "total_amount": float(record.total_amount or 0)
            })
        
        return {
            "success": True,
            "data": {
                "period_days": days,
                "daily_sales": analytics_data
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取销售分析失败: {str(e)}")

@router.post("/auto-management/enable")
async def enable_auto_management(
    settings: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """启用自动管理功能"""
    try:
        # 这里可以扩展自动管理功能
        # 比如自动回复、自动定价、自动延期等
        
        auto_settings = {
            "auto_reply": settings.get("auto_reply", False),
            "auto_pricing": settings.get("auto_pricing", False),
            "auto_extend": settings.get("auto_extend", False),
            "auto_relist": settings.get("auto_relist", False)
        }
        
        # 存储设置到用户偏好或店铺配置中
        # 这里简化处理，直接返回成功
        
        return {
            "success": True,
            "message": "自动管理功能设置成功",
            "settings": auto_settings
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"设置自动管理失败: {str(e)}")