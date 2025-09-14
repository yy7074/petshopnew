from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from ..core.database import get_db
from ..core.security import get_current_user, get_current_user_optional
from ..models.user import User
from ..schemas.local_service import (
    LocalServiceCreate, LocalServiceUpdate, LocalServiceResponse,
    LocalServiceListResponse, LocalServiceCommentCreate, LocalServiceCommentResponse,
    PetSocialPostCreate, PetSocialPostUpdate, PetSocialPostResponse,
    PetSocialPostListResponse, PetSocialCommentCreate, PetSocialCommentResponse,
    ServiceTypesResponse
)
from ..services.local_service_service import LocalServiceService

router = APIRouter()
local_service_service = LocalServiceService()


# 服务类型相关
@router.get("/types", response_model=ServiceTypesResponse)
async def get_service_types():
    """获取服务类型列表"""
    return await local_service_service.get_service_types()


# 同城服务相关
@router.post("/", response_model=LocalServiceResponse)
async def create_local_service(
    service_data: LocalServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建同城服务"""
    return await local_service_service.create_local_service(db, service_data, current_user.id)


@router.get("/", response_model=LocalServiceListResponse)
async def get_local_services(
    service_type: Optional[str] = Query(None, description="服务类型"),
    city: Optional[str] = Query(None, description="城市"),
    district: Optional[str] = Query(None, description="区县"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """获取同城服务列表"""
    user_id = current_user.id if current_user else None
    result = await local_service_service.get_local_services(
        db, service_type, city, district, keyword, page, page_size, user_id
    )
    return LocalServiceListResponse(**result)


@router.get("/{service_id}", response_model=LocalServiceResponse)
async def get_local_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """获取同城服务详情"""
    user_id = current_user.id if current_user else None
    service = await local_service_service.get_local_service_by_id(db, service_id, user_id)
    if not service:
        raise HTTPException(status_code=404, detail="服务不存在")
    return service


@router.put("/{service_id}", response_model=LocalServiceResponse)
async def update_local_service(
    service_id: int,
    service_data: LocalServiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新同城服务"""
    service = await local_service_service.update_local_service(db, service_id, service_data, current_user.id)
    if not service:
        raise HTTPException(status_code=404, detail="服务不存在或无权限")
    return service


@router.delete("/{service_id}")
async def delete_local_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除同城服务"""
    success = await local_service_service.delete_local_service(db, service_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="服务不存在或无权限")
    return {"message": "删除成功"}


# 同城服务评论相关
@router.post("/{service_id}/comments", response_model=LocalServiceCommentResponse)
async def create_local_service_comment(
    service_id: int,
    comment_data: LocalServiceCommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建同城服务评论"""
    return await local_service_service.create_local_service_comment(
        db, service_id, comment_data, current_user.id
    )


@router.get("/{service_id}/comments")
async def get_local_service_comments(
    service_id: int,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """获取同城服务评论列表"""
    return await local_service_service.get_local_service_comments(db, service_id, page, page_size)


# 同城服务点赞
@router.post("/{service_id}/like")
async def toggle_local_service_like(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """切换同城服务点赞状态"""
    return await local_service_service.toggle_local_service_like(db, service_id, current_user.id)


# 宠物交流相关
@router.post("/pet-social/posts", response_model=PetSocialPostResponse)
async def create_pet_social_post(
    post_data: PetSocialPostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建宠物交流帖子"""
    return await local_service_service.create_pet_social_post(db, post_data, current_user.id)


@router.get("/pet-social/posts", response_model=PetSocialPostListResponse)
async def get_pet_social_posts(
    category: Optional[str] = Query(None, description="分类"),
    city: Optional[str] = Query(None, description="城市"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """获取宠物交流帖子列表"""
    user_id = current_user.id if current_user else None
    result = await local_service_service.get_pet_social_posts(
        db, category, city, keyword, page, page_size, user_id
    )
    return PetSocialPostListResponse(**result)


@router.get("/pet-social/posts/{post_id}", response_model=PetSocialPostResponse)
async def get_pet_social_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """获取宠物交流帖子详情"""
    user_id = current_user.id if current_user else None
    post = await local_service_service.get_pet_social_post_by_id(db, post_id, user_id)
    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")
    return post


# 图片上传
@router.post("/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """上传图片"""
    try:
        return await local_service_service.upload_image(file, current_user.id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")


# 获取我的服务列表
@router.get("/my/services", response_model=LocalServiceListResponse)
async def get_my_local_services(
    service_type: Optional[str] = Query(None, description="服务类型"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取我的同城服务列表"""
    # 这里需要修改service来支持按用户ID筛选
    result = await local_service_service.get_local_services(
        db, service_type=service_type, page=page, page_size=page_size, user_id=current_user.id
    )
    return LocalServiceListResponse(**result)


# 获取热门服务
@router.get("/hot/services", response_model=LocalServiceListResponse)
async def get_hot_local_services(
    service_type: Optional[str] = Query(None, description="服务类型"),
    city: Optional[str] = Query(None, description="城市"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=50, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """获取热门同城服务"""
    user_id = current_user.id if current_user else None
    result = await local_service_service.get_local_services(
        db, service_type, city, None, None, page, page_size, user_id
    )
    return LocalServiceListResponse(**result)


# 按服务类型获取服务
@router.get("/by-type/{service_type}", response_model=LocalServiceListResponse)
async def get_services_by_type(
    service_type: str,
    city: Optional[str] = Query(None, description="城市"),
    district: Optional[str] = Query(None, description="区县"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """按服务类型获取服务列表"""
    user_id = current_user.id if current_user else None
    result = await local_service_service.get_local_services(
        db, service_type, city, district, None, page, page_size, user_id
    )
    return LocalServiceListResponse(**result)
