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
