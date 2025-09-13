from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional

from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..schemas.order import (
    OrderCreate, OrderResponse, OrderListResponse, OrderUpdate,
    PaymentCreate, PaymentResponse, LogisticsResponse
)
from ..services.order_service import OrderService
from ..services.payment_service import PaymentService
from ..services.logistics_service import LogisticsService

router = APIRouter()
order_service = OrderService()
payment_service = PaymentService()
logistics_service = LogisticsService()

@router.post("/", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建订单"""
    try:
        order = await order_service.create_order(db, order_data, current_user.id)
        
        # 后台任务：发送订单通知
        background_tasks.add_task(
            order_service.send_order_notification,
            db, order.id, "created"
        )
        
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="创建订单失败")

@router.get("/", response_model=OrderListResponse)
async def get_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, regex="^(pending|paid|shipped|delivered|completed|cancelled|refunded)$"),
    order_type: Optional[str] = Query(None, regex="^(buy|sell)$"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取订单列表"""
    return await order_service.get_user_orders(
        db, current_user.id, page, page_size, status, order_type, start_date, end_date
    )

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取订单详情"""
    order = await order_service.get_order_detail(db, order_id, current_user.id)
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order

@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    order_data: OrderUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新订单"""
    try:
        order = await order_service.update_order(db, order_id, order_data, current_user.id)
        if not order:
            raise HTTPException(status_code=404, detail="订单不存在或无权限修改")
        
        # 后台任务：发送状态变更通知
        if order_data.status:
            background_tasks.add_task(
                order_service.send_order_notification,
                db, order_id, order_data.status
            )
        
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{order_id}/status")
async def update_order_status(
    order_id: int,
    status: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新订单状态"""
    try:
        success = await order_service.update_order_status(db, order_id, status, current_user.id)
        if not success:
            raise HTTPException(status_code=404, detail="订单不存在或无权限修改")
        
        # 后台任务：发送状态变更通知
        background_tasks.add_task(
            order_service.send_order_notification,
            db, order_id, status
        )
        
        return {"message": "订单状态更新成功"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{order_id}/cancel")
async def cancel_order(
    order_id: int,
    background_tasks: BackgroundTasks,
    reason: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """取消订单"""
    try:
        success = await order_service.cancel_order(db, order_id, current_user.id, reason)
        if not success:
            raise HTTPException(status_code=404, detail="订单不存在或无法取消")
        
        # 后台任务：处理退款和通知
        background_tasks.add_task(
            order_service.process_order_cancellation,
            db, order_id
        )
        
        return {"message": "订单取消成功"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{order_id}/confirm")
async def confirm_order(
    order_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """确认收货"""
    try:
        success = await order_service.confirm_order(db, order_id, current_user.id)
        if not success:
            raise HTTPException(status_code=404, detail="订单不存在或无法确认收货")
        
        # 后台任务：完成订单处理
        background_tasks.add_task(
            order_service.complete_order_process,
            db, order_id
        )
        
        return {"message": "确认收货成功"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# 支付相关接口
@router.post("/payments/", response_model=PaymentResponse)
async def create_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建支付"""
    try:
        payment = await payment_service.create_payment(db, payment_data, current_user.id)
        return payment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="创建支付失败")

@router.get("/payments/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取支付详情"""
    payment = await payment_service.get_payment_detail(db, payment_id, current_user.id)
    if not payment:
        raise HTTPException(status_code=404, detail="支付记录不存在")
    return payment

@router.post("/payments/{payment_id}/notify")
async def payment_notify(
    payment_id: int,
    notify_data: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """支付回调通知"""
    try:
        success = await payment_service.handle_payment_notify(db, payment_id, notify_data)
        if success:
            # 后台任务：处理支付成功后续流程
            background_tasks.add_task(
                payment_service.process_payment_success,
                db, payment_id
            )
        return {"message": "通知处理成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="处理支付通知失败")

# 物流相关接口
@router.get("/{order_id}/logistics", response_model=LogisticsResponse)
async def get_order_logistics(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取订单物流信息"""
    logistics = await logistics_service.get_order_logistics(db, order_id, current_user.id)
    if not logistics:
        raise HTTPException(status_code=404, detail="物流信息不存在")
    return logistics

@router.put("/{order_id}/logistics")
async def update_logistics(
    order_id: int,
    tracking_number: str,
    logistics_company: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新物流信息（卖家操作）"""
    try:
        success = await logistics_service.update_logistics(
            db, order_id, tracking_number, logistics_company, current_user.id
        )
        if not success:
            raise HTTPException(status_code=404, detail="订单不存在或无权限修改")
        
        # 后台任务：发送发货通知
        background_tasks.add_task(
            logistics_service.send_shipping_notification,
            db, order_id
        )
        
        return {"message": "物流信息更新成功"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/statistics")
async def get_order_statistics(
    period: str = Query("month", regex="^(week|month|quarter|year)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取订单统计信息"""
    return await order_service.get_user_order_statistics(db, current_user.id, period)