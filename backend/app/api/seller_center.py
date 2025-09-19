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

@router.post("/orders/{order_id}/ship")
async def ship_order(
    order_id: int,
    shipping_data: Dict[str, str],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """商家发货"""
    try:
        from ..models.order import Order
        
        order = db.query(Order).filter(
            and_(
                Order.id == order_id,
                Order.seller_id == current_user.id
            )
        ).first()
        
        if not order:
            raise HTTPException(status_code=404, detail="订单不存在或无权限操作")
        
        if order.order_status != 2:  # 非待发货状态
            raise HTTPException(status_code=400, detail="订单状态不允许发货")
        
        tracking_number = shipping_data.get("tracking_number")
        if not tracking_number:
            raise HTTPException(status_code=400, detail="快递单号不能为空")
        
        # 更新订单状态
        order.order_status = 3  # 已发货
        order.tracking_number = tracking_number
        order.shipped_at = datetime.now()
        
        db.commit()
        
        return {
            "success": True,
            "message": "发货成功",
            "order_id": order_id,
            "tracking_number": tracking_number
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"发货失败: {str(e)}")

@router.get("/statistics")
async def get_seller_statistics(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取商家详细统计数据"""
    try:
        from ..models.order import Order
        from ..models.product import Product
        from sqlalchemy import and_, func
        from datetime import datetime, timedelta
        
        start_date = datetime.now() - timedelta(days=days)
        
        # 销售统计
        sales_stats = db.query(
            func.count(Order.id).label('total_orders'),
            func.sum(Order.total_amount).label('total_sales'),
            func.avg(Order.total_amount).label('avg_order_value')
        ).filter(
            and_(
                Order.seller_id == current_user.id,
                Order.created_at >= start_date,
                Order.payment_status == 2  # 已支付
            )
        ).first()
        
        # 订单状态统计
        order_status_stats = db.query(
            Order.order_status,
            func.count(Order.id).label('count')
        ).filter(
            and_(
                Order.seller_id == current_user.id,
                Order.created_at >= start_date
            )
        ).group_by(Order.order_status).all()
        
        # 商品统计
        product_stats = db.query(
            func.count(Product.id).label('total_products'),
            func.sum(func.case([(Product.status == 2, 1)], else_=0)).label('active_products'),
            func.sum(func.case([(Product.status == 4, 1)], else_=0)).label('inactive_products'),
            func.sum(Product.view_count).label('total_views')
        ).filter(Product.seller_id == current_user.id).first()
        
        # 热销商品
        top_products = db.query(
            Product.id,
            Product.title,
            Product.images,
            func.count(Order.id).label('sales_count'),
            func.sum(Order.total_amount).label('total_sales')
        ).join(Order, Product.id == Order.product_id).filter(
            and_(
                Product.seller_id == current_user.id,
                Order.created_at >= start_date,
                Order.payment_status == 2
            )
        ).group_by(Product.id).order_by(
            func.count(Order.id).desc()
        ).limit(5).all()
        
        # 组织返回数据
        order_status_dict = {
            1: 0,  # 待付款
            2: 0,  # 待发货
            3: 0,  # 已发货
            4: 0,  # 已完成
            5: 0,  # 已取消
        }
        
        for status_stat in order_status_stats:
            order_status_dict[status_stat.order_status] = status_stat.count
        
        top_products_list = []
        for product in top_products:
            top_products_list.append({
                "id": product.id,
                "name": product.title,
                "image": product.images[0] if product.images else None,
                "sales_count": product.sales_count,
                "total_sales": float(product.total_sales or 0)
            })
        
        return {
            "success": True,
            "data": {
                "total_sales": float(sales_stats.total_sales or 0),
                "total_orders": sales_stats.total_orders or 0,
                "avg_order_value": float(sales_stats.avg_order_value or 0),
                "pending_payment": order_status_dict[1],
                "pending_shipment": order_status_dict[2],
                "shipped": order_status_dict[3],
                "completed": order_status_dict[4],
                "cancelled": order_status_dict[5],
                "active_products": product_stats.active_products or 0,
                "inactive_products": product_stats.inactive_products or 0,
                "total_views": product_stats.total_views or 0,
                "top_products": top_products_list,
                "total_customers": 0,  # 待实现
                "new_customers": 0,  # 待实现
                "repeat_customers": 0,  # 待实现
                "customer_regions": [],  # 待实现
                "low_stock_products": 0  # 待实现
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计数据失败: {str(e)}")

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