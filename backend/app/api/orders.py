from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal
import time

from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..models.order import Order, Payment
from ..schemas.order import (
    OrderCreate, OrderResponse, OrderListResponse, OrderUpdate,
    PaymentCreate, PaymentResponse, LogisticsResponse
)
from ..services.order_service import OrderService
from ..services.payment_service import PaymentService
from ..services.logistics_service import LogisticsService
from ..services.alipay_service import AlipayService
from ..services.test_payment_service import TestPaymentService

router = APIRouter()
order_service = OrderService()
payment_service = PaymentService()
logistics_service = LogisticsService()
alipay_service = AlipayService()
test_payment_service = TestPaymentService()

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

# 支付宝支付接口
@router.post("/test/create")
async def create_test_order(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建测试订单"""
    try:
        # 创建测试订单
        order = Order(
            order_no=f"TEST_{int(time.time())}",
            buyer_id=current_user.id,
            seller_id=1,  # 测试卖家
            product_id=1,  # 测试商品
            final_price=0.01,  # 测试金额
            total_amount=0.01,
            shipping_fee=0.00,
            payment_method=1,  # 1:支付宝
            payment_status=1,  # 1:待支付
            order_status=1,  # 1:待支付
        )
        
        db.add(order)
        db.commit()
        db.refresh(order)
        
        # 创建订单项
        from ..models.order import OrderItem
        order_item = OrderItem(
            order_id=order.id,
            product_id=1,
            product_title="测试商品",
            product_image="https://picsum.photos/200/200?random=1",
            quantity=1,
            unit_price=0.01,
            total_price=0.01
        )
        
        db.add(order_item)
        db.commit()
        
        return {
            "success": True,
            "data": {
                "order_id": order.id,
                "order_no": order.order_no,
                "total_amount": str(order.total_amount)
            }
        }
    except Exception as e:
        print(f"创建测试订单失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"创建测试订单失败: {str(e)}")

@router.post("/{order_id}/alipay/app")
async def create_alipay_app_payment(
    order_id: int,
    notify_url: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建支付宝App支付"""
    try:
        # 使用真实支付宝服务
        payment_data = await alipay_service.create_payment(
            db, order_id, current_user.id, notify_url=notify_url
        )
        return {
            "success": True,
            "data": payment_data
        }
    except ValueError as e:
        print(f"支付宝支付ValueError: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"支付宝支付Exception: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"创建支付失败: {str(e)}")

@router.get("/payments/{payment_id}/alipay/query")
async def query_alipay_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """查询支付宝支付状态"""
    try:
        # 使用测试支付服务查询
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(status_code=404, detail="支付记录不存在")
            
        if payment.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="无权限查询此支付记录")
            
        # 模拟查询结果
        result = await test_payment_service.query_payment(payment.transaction_id)
        
        return {
            "success": True,
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"查询支付状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"查询支付状态失败: {str(e)}")

# 创建测试订单接口
@router.post("/test/create")
async def create_test_order(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建测试订单"""
    try:
        from ..models.order import Order
        from datetime import datetime
        import uuid
        
        # 创建测试订单
        test_order = Order(
            order_no=f"TEST{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4().int)[:6]}",
            buyer_id=current_user.id,
            seller_id=current_user.id,  # 自己卖给自己用于测试
            product_id=1,  # 假设存在商品ID 1
            final_price=0.01,
            shipping_fee=0.00,
            total_amount=0.01,
            order_status=1,  # 待支付
            payment_status=1,  # 待支付
            payment_method=1,  # 支付宝
            shipping_address={"name": "测试用户", "phone": "13800138000", "address": "测试地址"}
        )
        
        db.add(test_order)
        db.commit()
        db.refresh(test_order)
        
        return {
            "success": True,
            "message": "测试订单创建成功",
            "data": {
                "order_id": test_order.id,
                "order_no": test_order.order_no,
                "total_amount": test_order.total_amount
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建测试订单失败: {str(e)}")

@router.post("/{order_id}/alipay/web")
async def create_alipay_web_payment(
    order_id: int,
    return_url: Optional[str] = None,
    notify_url: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建支付宝网页支付"""
    try:
        payment_url = await alipay_service.create_web_payment(
            db, order_id, current_user.id, return_url, notify_url
        )
        return {
            "success": True,
            "payment_url": payment_url
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="创建支付失败")

@router.post("/payments/{payment_id}/alipay/notify")
async def alipay_notify(
    payment_id: int,
    notify_data: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """支付宝支付回调通知"""
    try:
        success = await alipay_service.handle_notify(db, payment_id, notify_data)
        if success:
            return "success"
        else:
            return "fail"
    except Exception as e:
        print(f"处理支付宝通知失败: {e}")
        return "fail"

@router.get("/payments/{payment_id}/alipay/query")
async def query_alipay_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """查询支付宝支付状态"""
    try:
        # 获取支付记录
        payment = db.query(Payment).filter(
            Payment.id == payment_id,
            Payment.user_id == current_user.id
        ).first()
        
        if not payment:
            raise HTTPException(status_code=404, detail="支付记录不存在")
            
        # 查询支付状态
        result = await alipay_service.query_payment(payment.transaction_id)
        return {
            "success": True,
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="查询支付状态失败")

@router.post("/payments/{payment_id}/alipay/refund")
async def create_alipay_refund(
    payment_id: int,
    refund_amount: Optional[float] = None,
    refund_reason: str = "用户申请退款",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """申请支付宝退款"""
    try:
        # 验证权限
        payment = db.query(Payment).filter(
            Payment.id == payment_id,
            Payment.user_id == current_user.id
        ).first()
        
        if not payment:
            raise HTTPException(status_code=404, detail="支付记录不存在")
            
        result = await alipay_service.refund(
            db, payment_id, 
            Decimal(str(refund_amount)) if refund_amount else None, 
            refund_reason
        )
        return result
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="申请退款失败")