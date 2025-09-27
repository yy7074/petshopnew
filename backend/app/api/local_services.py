from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..services.local_service import LocalService
from ..schemas.local_service import (
    # 宠物交流
    PetSocialPostCreate, PetSocialPostUpdate, PetSocialPostResponse, PetSocialPostListResponse,
    PetSocialCommentCreate, PetSocialCommentResponse,
    # 宠物配种
    PetBreedingInfoCreate, PetBreedingInfoUpdate, PetBreedingInfoResponse, PetBreedingInfoListResponse,
    # 本地宠店
    LocalPetStoreCreate, LocalPetStoreUpdate, LocalPetStoreResponse, LocalPetStoreListResponse,
    # 鱼缸造景
    AquariumDesignServiceCreate, AquariumDesignServiceUpdate, AquariumDesignServiceResponse, AquariumDesignServiceListResponse,
    # 上门服务
    DoorServiceCreate, DoorServiceUpdate, DoorServiceResponse, DoorServiceListResponse,
    # 宠物估价
    PetValuationServiceCreate, PetValuationServiceResponse, PetValuationServiceListResponse,
    # 附近发现
    NearbyItemCreate, NearbyItemUpdate, NearbyItemResponse, NearbyItemListResponse,
    # 统计
    ServiceStatsResponse
)

router = APIRouter()
local_service = LocalService()

# ==================== 宠物交流相关接口 ====================

@router.post("/social-posts", response_model=PetSocialPostResponse)
async def create_social_post(
    post_data: PetSocialPostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建宠物交流帖子"""
    try:
        return await local_service.create_social_post(db, post_data, current_user.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/social-posts", response_model=PetSocialPostListResponse)
async def get_social_posts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    pet_type: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """获取宠物交流帖子列表"""
    try:
        return await local_service.get_social_posts(db, page, page_size, pet_type, location)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/social-posts/{post_id}", response_model=PetSocialPostResponse)
async def get_social_post_detail(
    post_id: int,
    db: Session = Depends(get_db)
):
    """获取帖子详情"""
    try:
        post = await local_service.get_social_post_detail(db, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="帖子不存在")
        return post
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/social-posts/{post_id}/comments", response_model=PetSocialCommentResponse)
async def create_social_comment(
    post_id: int,
    comment_data: PetSocialCommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建评论"""
    try:
        return await local_service.create_social_comment(db, post_id, comment_data, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/social-posts/{post_id}/like")
async def like_social_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """点赞/取消点赞帖子"""
    try:
        result = await local_service.toggle_post_like(db, post_id, current_user.id)
        return {
            "success": True,
            "liked": result["liked"],
            "like_count": result["like_count"],
            "message": "点赞成功" if result["liked"] else "取消点赞成功"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/social-posts/search")
async def search_social_posts(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    pet_type: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    sort_by: str = Query("created_at", description="排序方式：created_at, like_count, comment_count"),
    sort_order: str = Query("desc", description="排序顺序：asc, desc"),
    db: Session = Depends(get_db)
):
    """搜索宠物社交帖子"""
    try:
        result = await local_service.search_social_posts(
            db, q, page, page_size, pet_type, location, sort_by, sort_order
        )
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/social-posts/{post_id}/likes")
async def get_post_likes(
    post_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取帖子点赞列表"""
    try:
        result = await local_service.get_post_likes(db, post_id, page, page_size)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 宠物配种相关接口 ====================

@router.post("/breeding-info", response_model=PetBreedingInfoResponse)
async def create_breeding_info(
    breeding_data: PetBreedingInfoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建宠物配种信息"""
    try:
        return await local_service.create_breeding_info(db, breeding_data, current_user.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/breeding-info", response_model=PetBreedingInfoListResponse)
async def get_breeding_info_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    pet_type: Optional[str] = Query(None),
    breed: Optional[str] = Query(None),
    gender: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """获取宠物配种信息列表"""
    try:
        return await local_service.get_breeding_info_list(db, page, page_size, pet_type, breed, gender, location)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 本地宠店相关接口 ====================

@router.get("/pet-stores", response_model=LocalPetStoreListResponse)
async def get_local_pet_stores(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    location: Optional[str] = Query(None),
    service_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """获取本地宠店列表"""
    try:
        return await local_service.get_local_pet_stores(db, page, page_size, location, service_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 鱼缸造景相关接口 ====================

@router.post("/aquarium-design", response_model=AquariumDesignServiceResponse)
async def create_aquarium_design_service(
    design_data: AquariumDesignServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建鱼缸造景服务"""
    try:
        return await local_service.create_aquarium_design_service(db, design_data, current_user.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/aquarium-design", response_model=AquariumDesignServiceListResponse)
async def get_aquarium_design_services(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    location: Optional[str] = Query(None),
    style: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """获取鱼缸造景服务列表"""
    try:
        return await local_service.get_aquarium_design_services(db, page, page_size, location, style)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 上门服务相关接口 ====================

@router.post("/door-services", response_model=DoorServiceResponse)
async def create_door_service(
    service_data: DoorServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建上门服务"""
    try:
        return await local_service.create_door_service(db, service_data, current_user.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/door-services", response_model=DoorServiceListResponse)
async def get_door_services(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service_type: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """获取上门服务列表"""
    try:
        return await local_service.get_door_services(db, page, page_size, service_type, location)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 宠物估价相关接口 ====================

@router.post("/pet-valuation", response_model=PetValuationServiceResponse)
async def create_pet_valuation(
    valuation_data: PetValuationServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建宠物估价申请"""
    try:
        return await local_service.create_pet_valuation(db, valuation_data, current_user.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pet-valuation", response_model=PetValuationServiceListResponse)
async def get_pet_valuations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取我的宠物估价列表"""
    try:
        # 这里可以添加只获取当前用户的估价记录的逻辑
        # 暂时返回空列表，实际实现时需要在service中添加相应方法
        return PetValuationServiceListResponse(
            items=[],
            total=0,
            page=page,
            page_size=page_size,
            total_pages=0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 附近发现相关接口 ====================

@router.post("/nearby-items", response_model=NearbyItemResponse)
async def create_nearby_item(
    item_data: NearbyItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建附近发现项目"""
    try:
        return await local_service.create_nearby_item(db, item_data, current_user.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/nearby-items", response_model=NearbyItemListResponse)
async def get_nearby_items(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    latitude: Optional[float] = Query(None),
    longitude: Optional[float] = Query(None),
    radius: Optional[float] = Query(None, description="搜索半径(度)"),
    db: Session = Depends(get_db)
):
    """获取附近发现列表"""
    try:
        return await local_service.get_nearby_items(
            db, page, page_size, category, location, latitude, longitude, radius
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 同城快取相关接口 ====================

@router.get("/pickup-services", response_model=dict)
async def get_pickup_services(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    location: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """获取同城快取服务列表"""
    # 暂时返回模拟数据
    return {
        "items": [
            {
                "id": 1,
                "product_name": "金毛幼犬",
                "pickup_location": "朝阳区望京SOHO",
                "available_times": ["9:00-12:00", "14:00-18:00"],
                "contact_person": "张先生",
                "contact_phone": "138****5678",
                "notes": "请提前30分钟联系"
            }
        ],
        "total": 1,
        "page": page,
        "page_size": page_size,
        "total_pages": 1
    }

# ==================== 统计相关接口 ====================

@router.get("/stats", response_model=ServiceStatsResponse)
async def get_service_stats(
    db: Session = Depends(get_db)
):
    """获取服务统计数据"""
    try:
        return await local_service.get_service_stats(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 回收查询相关路由 ====================

@router.get("/recycling-items")
async def get_recycling_items(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    db: Session = Depends(get_db)
):
    """获取回收物品列表"""
    try:
        return await local_service.get_recycling_items(
            db=db,
            page=page,
            page_size=page_size,
            category=category,
            location=location,
            status=status,
            keyword=keyword,
            sort_by=sort_by,
            sort_order=sort_order
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/recycling-items")
async def create_recycling_item(
    item_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建回收物品"""
    try:
        return await local_service.create_recycling_item(
            db=db,
            item_data=item_data,
            user_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recycling-items/{item_id}")
async def get_recycling_item_detail(
    item_id: int,
    db: Session = Depends(get_db)
):
    """获取回收物品详情"""
    try:
        return await local_service.get_recycling_item_detail(db, item_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/recycling-orders")
async def create_recycling_order(
    order_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建回收订单"""
    try:
        return await local_service.create_recycling_order(
            db=db,
            order_data=order_data,
            buyer_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recycling-orders")
async def get_recycling_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    order_type: str = Query("all"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户的回收订单"""
    try:
        return await local_service.get_recycling_orders(
            db=db,
            user_id=current_user.id,
            page=page,
            page_size=page_size,
            status=status,
            order_type=order_type
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 合作方代理相关路由 ====================

@router.post("/partner-applications")
async def create_partner_application(
    application_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建合作方代理申请"""
    try:
        return await local_service.create_partner_application(
            db=db,
            application_data=application_data,
            user_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/partner-applications")
async def get_partner_applications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户的合作方代理申请列表"""
    try:
        return await local_service.get_user_partner_applications(
            db=db,
            user_id=current_user.id,
            page=page,
            page_size=page_size
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/partner-applications/{application_id}")
async def get_partner_application_detail(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取合作方代理申请详情"""
    try:
        application = await local_service.get_partner_application_detail(
            db=db,
            application_id=application_id
        )
        
        # 检查权限：只能查看自己的申请
        if application['user_id'] != current_user.id:
            raise HTTPException(status_code=403, detail="无权访问此申请")
        
        return application
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

