from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.follow_service import FollowService, BrowseHistoryService, UserInfoService
from app.schemas.follow import (
    FollowResponse, FollowListResponse, BrowseHistoryResponse,
    UserDetailResponse, UserInfoUpdate
)
from typing import List

router = APIRouter()


# 关注相关接口
@router.post("/follow/{user_id}", response_model=FollowResponse)
async def follow_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """关注用户"""
    service = FollowService(db)
    return service.follow_user(current_user.id, user_id)


@router.delete("/follow/{user_id}", response_model=FollowResponse)
async def unfollow_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """取消关注用户"""
    service = FollowService(db)
    return service.unfollow_user(current_user.id, user_id)


@router.get("/following", response_model=FollowListResponse)
async def get_following_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取关注列表"""
    service = FollowService(db)
    return service.get_following_list(current_user.id, page, page_size)


@router.get("/followers", response_model=FollowListResponse)
async def get_followers_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取粉丝列表"""
    service = FollowService(db)
    return service.get_followers_list(current_user.id, page, page_size)


# 浏览历史相关接口
@router.post("/browse-history/{product_id}")
async def add_browse_history(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """添加浏览历史"""
    # 这里需要根据product_id获取商品信息
    # 简化实现，使用模拟数据
    product_data = {
        'title': '商品标题',
        'image': 'https://picsum.photos/200/200',
        'price': '1000.00',
        'seller_name': '卖家名称',
        'seller_location': '北京朝阳',
        'type': 'auction',
        'status': '拍卖中'
    }
    
    service = BrowseHistoryService(db)
    service.add_browse_history(current_user.id, product_id, product_data)
    return {"message": "添加浏览历史成功"}


@router.get("/browse-history", response_model=BrowseHistoryResponse)
async def get_browse_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取浏览历史"""
    service = BrowseHistoryService(db)
    return service.get_browse_history(current_user.id, page, page_size)


@router.get("/browse-history/today")
async def get_today_browse_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取今天的浏览历史"""
    service = BrowseHistoryService(db)
    items = service.get_today_browse_history(current_user.id)
    return {"items": items}


@router.get("/browse-history/yesterday")
async def get_yesterday_browse_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取昨天的浏览历史"""
    service = BrowseHistoryService(db)
    items = service.get_yesterday_browse_history(current_user.id)
    return {"items": items}


@router.delete("/browse-history/{history_id}")
async def delete_browse_history(
    history_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除单个浏览历史"""
    service = BrowseHistoryService(db)
    success = service.delete_browse_history(current_user.id, history_id)
    if not success:
        raise HTTPException(status_code=404, detail="浏览历史不存在")
    return {"message": "删除成功"}


@router.delete("/browse-history")
async def clear_browse_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """清空所有浏览历史"""
    service = BrowseHistoryService(db)
    service.clear_browse_history(current_user.id)
    return {"message": "清空成功"}


# 用户统计信息接口
@router.get("/user/stats")
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户统计信息（关注数、粉丝数、浏览历史数）"""
    try:
        # 关注数
        following_count = db.query(UserFollow).filter(UserFollow.follower_id == current_user.id).count()
        
        # 粉丝数
        follower_count = db.query(UserFollow).filter(UserFollow.following_id == current_user.id).count()
        
        # 浏览历史数
        browse_history_count = db.query(BrowseHistory).filter(BrowseHistory.user_id == current_user.id).count()
        
        return {
            "success": True,
            "data": {
                "following_count": following_count,
                "follower_count": follower_count,
                "browse_history_count": browse_history_count
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户统计失败: {str(e)}")


# 用户信息相关接口
@router.get("/user/detail", response_model=UserDetailResponse)
async def get_user_detail(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户详细信息"""
    service = UserInfoService(db)
    user_detail = service.get_user_detail(current_user.id)
    if not user_detail:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user_detail


@router.put("/user/info")
async def update_user_info(
    user_info: UserInfoUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新用户信息"""
    service = UserInfoService(db)
    
    # 转换为字典，过滤None值
    update_data = {k: v for k, v in user_info.dict().items() if v is not None}
    
    success = service.update_user_info(current_user.id, update_data)
    if not success:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return {"message": "更新成功"}


@router.post("/user/avatar")
async def upload_avatar(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """上传头像"""
    # 这里应该处理文件上传
    # 简化实现，返回模拟的头像URL
    avatar_url = f"https://picsum.photos/200/200?random={current_user.id}"
    
    service = UserInfoService(db)
    success = service.update_user_info(current_user.id, {"avatar_url": avatar_url})
    
    if not success:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return {"avatar_url": avatar_url, "message": "头像上传成功"}