from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from decimal import Decimal

from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..services.auction_service import AuctionService
from ..services.order_service import OrderService
from ..services.alipay_service import AlipayService

router = APIRouter()
auction_service = AuctionService()
order_service = OrderService()
alipay_service = AlipayService()

@router.get("/{product_id}/status")
async def get_auction_status(
    product_id: int,
    db: Session = Depends(get_db)
):
    """获取拍卖状态"""
    try:
        return await auction_service.get_auction_status(db, product_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="获取拍卖状态失败")

@router.post("/{product_id}/end")
async def manual_end_auction(
    product_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """手动结束拍卖（卖家操作）"""
    try:
        result = await auction_service.manual_end_auction(db, product_id, current_user.id)
        return {
            "success": True,
            "message": "拍卖结束成功",
            "data": result
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="结束拍卖失败")

@router.post("/{product_id}/winner-order")
async def create_winner_order(
    product_id: int,
    shipping_address: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """拍卖获胜者创建订单（补充收货地址）"""
    try:
        from ..models.product import Product, Bid
        from ..models.order import Order
        from sqlalchemy import and_, desc
        
        # 验证用户是否为该商品的获胜者
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="商品不存在")
        
        if product.status != 3:  # 已结束
            raise HTTPException(status_code=400, detail="拍卖未结束")
        
        # 查找获胜的出价
        winning_bid = db.query(Bid).filter(
            and_(
                Bid.product_id == product_id,
                Bid.bidder_id == current_user.id,
                Bid.status == 1  # 获胜
            )
        ).first()
        
        if not winning_bid:
            raise HTTPException(status_code=403, detail="您不是该拍卖的获胜者")
        
        # 查找是否已有订单
        existing_order = db.query(Order).filter(
            and_(
                Order.product_id == product_id,
                Order.buyer_id == current_user.id
            )
        ).first()
        
        if existing_order:
            # 更新收货地址
            existing_order.shipping_address = shipping_address
            db.commit()
            
            return {
                "success": True,
                "message": "订单信息已更新",
                "data": {
                    "order_id": existing_order.id,
                    "order_no": existing_order.order_no,
                    "total_amount": str(existing_order.total_amount)
                }
            }
        else:
            raise HTTPException(status_code=404, detail="订单不存在，请联系客服")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建订单失败: {str(e)}")

@router.post("/{product_id}/winner-order/{order_id}/pay")
async def pay_winner_order(
    product_id: int,
    order_id: int,
    notify_url: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """拍卖获胜者支付订单"""
    try:
        from ..models.order import Order
        from sqlalchemy import and_
        
        # 验证订单
        order = db.query(Order).filter(
            and_(
                Order.id == order_id,
                Order.product_id == product_id,
                Order.buyer_id == current_user.id,
                Order.payment_status == 1  # 待支付
            )
        ).first()
        
        if not order:
            raise HTTPException(status_code=404, detail="订单不存在或已支付")
        
        # 创建支付
        payment_data = await alipay_service.create_payment(
            db, order_id, current_user.id, notify_url=notify_url
        )
        
        return {
            "success": True,
            "message": "支付创建成功",
            "data": payment_data
        }
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建支付失败: {str(e)}")

@router.get("/my/winning")
async def get_my_winning_auctions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取我中标的拍卖"""
    try:
        from ..models.product import Product, Bid
        from ..models.order import Order
        from sqlalchemy import and_, desc
        
        # 查找我获胜的出价
        winning_bids_query = db.query(Bid).filter(
            and_(
                Bid.bidder_id == current_user.id,
                Bid.status == 1  # 获胜
            )
        ).order_by(desc(Bid.created_at))
        
        total = winning_bids_query.count()
        winning_bids = winning_bids_query.offset((page - 1) * page_size).limit(page_size).all()
        
        results = []
        for bid in winning_bids:
            product = db.query(Product).filter(Product.id == bid.product_id).first()
            order = db.query(Order).filter(
                and_(
                    Order.product_id == bid.product_id,
                    Order.buyer_id == current_user.id
                )
            ).first()
            
            results.append({
                "product_id": product.id,
                "product_title": product.title,
                "product_images": product.images,
                "winning_amount": str(bid.bid_amount),
                "bid_time": bid.created_at.isoformat(),
                "order_id": order.id if order else None,
                "order_no": order.order_no if order else None,
                "payment_status": order.payment_status if order else None,
                "order_status": order.order_status if order else None
            })
        
        return {
            "items": results,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="获取中标记录失败")

@router.post("/batch/check-expired")
async def batch_check_expired_auctions(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """批量检查过期拍卖（管理员或定时任务）"""
    try:
        # 这里可以添加权限检查，只允许管理员或系统调用
        results = await auction_service.check_and_end_auctions(db)
        
        return {
            "success": True,
            "message": f"处理了 {len(results)} 个过期拍卖",
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="批量处理拍卖失败")

@router.get("/rules")
async def get_auction_rules():
    """获取拍卖标准化规则"""
    try:
        return await auction_service.get_auction_rules()
    except Exception as e:
        raise HTTPException(status_code=500, detail="获取拍卖规则失败")

@router.post("/validate-setup")
async def validate_auction_setup(
    auction_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """验证拍卖设置"""
    try:
        # 处理日期时间字符串
        if 'auction_start_time' in auction_data and isinstance(auction_data['auction_start_time'], str):
            from datetime import datetime
            auction_data['auction_start_time'] = datetime.fromisoformat(auction_data['auction_start_time'])
        if 'auction_end_time' in auction_data and isinstance(auction_data['auction_end_time'], str):
            from datetime import datetime
            auction_data['auction_end_time'] = datetime.fromisoformat(auction_data['auction_end_time'])
        
        result = await auction_service.validate_auction_setup(db, auction_data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="验证拍卖设置失败")

@router.post("/{product_id}/bid-enhanced")
async def place_enhanced_bid(
    product_id: int,
    bid_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """增强出价接口（支持自动延时等功能）"""
    try:
        bid_amount = Decimal(str(bid_data.get('bid_amount', 0)))
        
        result = await auction_service.process_bid_with_auto_extend(
            db, product_id, bid_amount, current_user.id
        )
        
        return {
            "success": True,
            "message": "出价成功",
            "data": result
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"出价失败: {str(e)}")