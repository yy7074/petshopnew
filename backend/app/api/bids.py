from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal

from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..schemas.bid import BidCreate, BidResponse, BidListResponse, AutoBidCreate
from ..services.bid_service import BidService
from ..services.notification_service import NotificationService

router = APIRouter()
bid_service = BidService()
notification_service = NotificationService()

@router.post("/", response_model=BidResponse)
async def place_bid(
    bid_data: BidCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """出价竞拍"""
    try:
        bid = await bid_service.place_bid(db, bid_data, current_user.id)
        
        # 暂时注释掉通知服务，避免错误
        # background_tasks.add_task(
        #     notification_service.send_bid_notification,
        #     db, bid.product_id, bid.amount, current_user.username
        # )
        
        return bid
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        error_detail = f"出价失败: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

@router.get("/product/{product_id}", response_model=BidListResponse)
async def get_product_bids(
    product_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取商品的出价记录"""
    return await bid_service.get_product_bids(db, product_id, page, page_size)

@router.get("/my", response_model=BidListResponse)
async def get_my_bids(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, regex="^(active|won|lost|cancelled)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取我的出价记录"""
    return await bid_service.get_user_bids(db, current_user.id, page, page_size, status)

@router.get("/winning", response_model=BidListResponse)
async def get_winning_bids(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取我正在领先的竞拍"""
    return await bid_service.get_winning_bids(db, current_user.id, page, page_size)

@router.get("/history", response_model=BidListResponse)
async def get_bid_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    product_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取竞拍历史"""
    return await bid_service.get_bid_history(
        db, current_user.id, page, page_size, product_id, start_date, end_date
    )

@router.post("/auto", response_model=dict)
async def create_auto_bid(
    auto_bid_data: AutoBidCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """设置自动出价"""
    try:
        result = await bid_service.create_auto_bid(db, auto_bid_data, current_user.id)
        return {"message": "自动出价设置成功", "auto_bid_id": result.id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/auto/my")
async def get_my_auto_bids(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query("active", regex="^(active|paused|completed|cancelled)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取我的自动出价设置"""
    return await bid_service.get_user_auto_bids(db, current_user.id, page, page_size, status)

@router.put("/auto/{auto_bid_id}/pause")
async def pause_auto_bid(
    auto_bid_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """暂停自动出价"""
    success = await bid_service.pause_auto_bid(db, auto_bid_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="自动出价不存在或无权限操作")
    return {"message": "自动出价已暂停"}

@router.put("/auto/{auto_bid_id}/resume")
async def resume_auto_bid(
    auto_bid_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """恢复自动出价"""
    success = await bid_service.resume_auto_bid(db, auto_bid_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="自动出价不存在或无权限操作")
    return {"message": "自动出价已恢复"}

@router.delete("/auto/{auto_bid_id}")
async def cancel_auto_bid(
    auto_bid_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """取消自动出价"""
    success = await bid_service.cancel_auto_bid(db, auto_bid_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="自动出价不存在或无权限操作")
    return {"message": "自动出价已取消"}

@router.get("/statistics")
async def get_bid_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取出价统计信息"""
    return await bid_service.get_user_bid_statistics(db, current_user.id)

@router.get("/{bid_id}", response_model=BidResponse)
async def get_bid_detail(
    bid_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取出价详情"""
    bid = await bid_service.get_bid_detail(db, bid_id, current_user.id)
    if not bid:
        raise HTTPException(status_code=404, detail="出价记录不存在")
    return bid

@router.delete("/{bid_id}")
async def cancel_bid(
    bid_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """取消出价（仅在特定条件下允许）"""
    try:
        success = await bid_service.cancel_bid(db, bid_id, current_user.id)
        if not success:
            raise HTTPException(status_code=404, detail="出价记录不存在或无法取消")
        return {"message": "出价已取消"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))