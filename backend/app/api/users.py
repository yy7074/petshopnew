from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/store-status")
async def get_user_store_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户店铺状态"""
    from ..models.store import Store
    from ..models.store_application import StoreApplication
    
    # 检查用户是否有店铺
    store = db.query(Store).filter(Store.owner_id == current_user.id).first()
    has_store = store is not None
    
    # 获取用户的店铺申请状态
    application = db.query(StoreApplication).filter(
        StoreApplication.user_id == current_user.id
    ).order_by(StoreApplication.created_at.desc()).first()
    
    application_status = None
    if application:
        application_status = {
            "id": application.id,
            "status": application.status,
            "store_name": application.store_name,
            "store_type": application.store_type,
            "created_at": application.created_at.isoformat(),
            "updated_at": application.updated_at.isoformat() if application.updated_at else None,
        }
    
    return {
        "has_store": has_store,
        "store": {
            "id": store.id,
            "name": store.name,
            "description": store.description,
            "is_open": store.is_open,
            "verified": store.verified,
        } if store else None,
        "application": application_status,
        "is_seller": current_user.is_seller,
    }

@router.put("/seller-status")
async def update_seller_status(
    is_seller: bool,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新用户卖家状态"""
    # 如果要设置为卖家，需要检查是否有店铺
    if is_seller:
        from ..models.store import Store
        store = db.query(Store).filter(Store.owner_id == current_user.id).first()
        if not store:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="您还没有店铺，无法切换到卖家模式"
            )
    
    # 更新用户状态
    current_user.is_seller = is_seller
    db.commit()
    db.refresh(current_user)
    
    return {
        "message": f"已切换到{'卖家' if is_seller else '买家'}模式",
        "is_seller": current_user.is_seller
    }

# 兼容性端点：为Flutter应用提供用户中标拍卖接口
@router.get("/auctions/winning")
async def get_user_winning_auctions(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户中标的拍卖（兼容性端点）"""
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
