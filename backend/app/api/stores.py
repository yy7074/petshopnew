from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..core.database import get_db
from ..core.security import get_current_user, get_current_user_optional
from ..models.user import User
from ..schemas.store import (
    StoreCreate, StoreUpdate, StoreResponse, StoreListResponse,
    StoreFollowRequest, StoreReviewCreate, StoreReviewResponse,
    StoreReviewListResponse, StoreStatsResponse
)
from ..services.store_service import StoreService

router = APIRouter()
store_service = StoreService()

@router.get("/by-seller/{seller_id}", response_model=StoreResponse)
async def get_store_by_seller(
    seller_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """通过卖家ID获取店铺信息"""
    try:
        # 验证seller_id参数
        if seller_id <= 0:
            raise HTTPException(status_code=400, detail="无效的卖家ID")
            
        user_id = current_user.id if current_user else None
        store = await store_service.get_store_by_owner(db, seller_id)
        if not store:
            raise HTTPException(status_code=404, detail="店铺不存在")
        
        # 如果有用户登录，检查关注状态
        if user_id:
            store = await store_service.get_store_by_id(db, store.id, user_id)
        
        return store
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{store_id}", response_model=StoreResponse)
async def get_store(
    store_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """获取店铺详情"""
    try:
        # 验证store_id参数
        if store_id <= 0:
            raise HTTPException(status_code=400, detail="无效的店铺ID")
            
        user_id = current_user.id if current_user else None
        store = await store_service.get_store_by_id(db, store_id, user_id)
        if not store:
            raise HTTPException(status_code=404, detail="店铺不存在")
        return store
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=StoreResponse)
async def create_store(
    store_data: StoreCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建店铺"""
    try:
        store = await store_service.create_store(db, store_data, current_user.id)
        return store
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{store_id}", response_model=StoreResponse)
async def update_store(
    store_id: int,
    store_data: StoreUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新店铺信息"""
    try:
        store = await store_service.update_store(db, store_id, store_data, current_user.id)
        return store
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{store_id}/products")
async def get_store_products(
    store_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = None,
    status: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """获取店铺商品列表"""
    try:
        # 验证store_id参数
        if store_id <= 0:
            raise HTTPException(status_code=400, detail="无效的店铺ID")
            
        result = await store_service.get_store_products(
            db, store_id, page, page_size, category_id, status
        )
        return result
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{store_id}/follow")
async def follow_store(
    store_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """关注店铺"""
    try:
        # 验证store_id参数
        if store_id <= 0:
            raise HTTPException(status_code=400, detail="无效的店铺ID")
            
        success = await store_service.follow_store(db, store_id, current_user.id)
        if success:
            return {"message": "关注成功"}
        else:
            return {"message": "已经关注过了"}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{store_id}/follow")
async def unfollow_store(
    store_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """取消关注店铺"""
    try:
        # 验证store_id参数
        if store_id <= 0:
            raise HTTPException(status_code=400, detail="无效的店铺ID")
            
        success = await store_service.unfollow_store(db, store_id, current_user.id)
        if success:
            return {"message": "取消关注成功"}
        else:
            return {"message": "未关注该店铺"}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{store_id}/reviews", response_model=StoreReviewListResponse)
async def get_store_reviews(
    store_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    rating_filter: Optional[int] = Query(None, ge=1, le=5),
    db: Session = Depends(get_db)
):
    """获取店铺评价列表"""
    try:
        # 验证store_id参数
        if store_id <= 0:
            raise HTTPException(status_code=400, detail="无效的店铺ID")
            
        reviews = await store_service.get_store_reviews(
            db, store_id, page, page_size, rating_filter
        )
        return reviews
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{store_id}/stats", response_model=StoreStatsResponse)
async def get_store_stats(
    store_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取店铺统计信息（仅店主）"""
    try:
        # 验证store_id参数
        if store_id <= 0:
            raise HTTPException(status_code=400, detail="无效的店铺ID")
            
        stats = await store_service.get_store_stats(db, store_id, current_user.id)
        return stats
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))