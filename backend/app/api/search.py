from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..core.database import get_db
from ..core.security import get_current_user, get_current_user_optional
from ..models.user import User
from ..schemas.search import SearchResponse, SearchSuggestionResponse, HotSearchResponse
from ..services.search_service import SearchService

router = APIRouter()
search_service = SearchService()

@router.get("/", response_model=SearchResponse)
async def search_products(
    keyword: str = Query(..., min_length=1, max_length=100),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: Optional[str] = Query("relevance", regex="^(relevance|price|created_at|end_time|popularity)$"),
    sort_order: Optional[str] = Query("desc", regex="^(asc|desc)$"),
    auction_type: Optional[str] = Query(None, regex="^(auction|fixed_price|both)$"),
    location: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """搜索商品"""
    try:
        result = await search_service.search_products(
            db=db,
            keyword=keyword,
            page=page,
            page_size=page_size,
            category_id=category_id,
            min_price=min_price,
            max_price=max_price,
            sort_by=sort_by,
            sort_order=sort_order,
            auction_type=auction_type,
            location=location,
            user_id=current_user.id if current_user else None
        )
        
        # 保存搜索历史
        if current_user:
            await search_service.save_search_history(db, current_user.id, keyword)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail="搜索失败")

@router.get("/suggestions", response_model=List[SearchSuggestionResponse])
async def get_search_suggestions(
    keyword: str = Query(..., min_length=1, max_length=50),
    limit: int = Query(10, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """获取搜索建议"""
    return await search_service.get_search_suggestions(db, keyword, limit)

@router.get("/hot", response_model=List[HotSearchResponse])
async def get_hot_searches(
    limit: int = Query(10, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """获取热门搜索"""
    return await search_service.get_hot_searches(db, limit)

@router.get("/history", response_model=List[str])
async def get_search_history(
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户搜索历史"""
    return await search_service.get_user_search_history(db, current_user.id, limit)

@router.post("/history")
async def save_search_history(
    keyword: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """保存搜索历史"""
    await search_service.save_search_history(db, current_user.id, keyword)
    return {"message": "搜索历史保存成功"}

@router.delete("/history")
async def clear_search_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """清除搜索历史"""
    await search_service.clear_search_history(db, current_user.id)
    return {"message": "搜索历史清除成功"}

@router.delete("/history/{keyword}")
async def delete_search_history_item(
    keyword: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除单条搜索历史"""
    await search_service.delete_search_history_item(db, current_user.id, keyword)
    return {"message": "搜索历史删除成功"}

@router.get("/filters")
async def get_search_filters(
    keyword: Optional[str] = None,
    category_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """获取搜索筛选选项"""
    return await search_service.get_search_filters(db, keyword, category_id)

@router.get("/trending")
async def get_trending_keywords(
    period: str = Query("day", regex="^(hour|day|week|month)$"),
    limit: int = Query(10, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """获取趋势关键词"""
    return await search_service.get_trending_keywords(db, period, limit)

@router.get("/categories/{category_id}/suggestions")
async def get_category_suggestions(
    category_id: int,
    limit: int = Query(10, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """获取分类相关搜索建议"""
    return await search_service.get_category_suggestions(db, category_id, limit)

@router.get("/autocomplete")
async def autocomplete_search(
    q: str = Query(..., min_length=1, max_length=50),
    type: str = Query("all", regex="^(all|products|categories|brands|users)$"),
    limit: int = Query(10, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """搜索自动完成"""
    return await search_service.autocomplete_search(db, q, type, limit)