"""
启动广告API路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional
from datetime import datetime
import os
import uuid

from app.core.database import get_db
from app.core.security import get_admin_user, get_current_user
from fastapi.security import HTTPBearer
from typing import Optional

# 临时的简单权限验证（开发环境）
security = HTTPBearer(auto_error=False)

def get_admin_user_simple(token: Optional[str] = Depends(security)):
    """简单的管理员权限验证（开发环境）"""
    # 开发环境：跳过严格验证
    if not token:
        # 如果没有token，也允许访问（开发环境）
        pass
    elif token.credentials != "admin-token":
        # 如果有token但不正确，返回错误
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    
    # 返回一个模拟的管理员用户对象
    class MockAdmin:
        id = 1
        username = "admin"
        is_admin = True
    return MockAdmin()
from app.models.splash_ad import SplashAd, AdStatus, AdType
from app.models.user import User
from app.schemas.splash_ad import (
    SplashAdCreate, SplashAdUpdate, SplashAdResponse, 
    SplashAdListResponse, SplashAdStatsUpdate, SplashAdClientResponse
)

router = APIRouter()

@router.post("/splash-ads", response_model=SplashAdResponse, summary="创建启动广告")
async def create_splash_ad(
    ad_data: SplashAdCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user_simple)
):
    """创建新的启动广告"""
    
    # 验证广告内容
    if ad_data.ad_type == AdType.IMAGE and not ad_data.image_url:
        raise HTTPException(status_code=400, detail="图片广告必须提供图片URL")
    
    if ad_data.ad_type == AdType.VIDEO and not ad_data.video_url:
        raise HTTPException(status_code=400, detail="视频广告必须提供视频URL")
    
    # 创建广告
    db_ad = SplashAd(**ad_data.dict())
    db.add(db_ad)
    db.commit()
    db.refresh(db_ad)
    
    return db_ad

@router.get("/splash-ads", response_model=SplashAdListResponse, summary="获取启动广告列表")
async def get_splash_ads(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    status: Optional[AdStatus] = Query(None, description="广告状态筛选"),
    ad_type: Optional[AdType] = Query(None, description="广告类型筛选"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user_simple)
):
    """获取启动广告列表"""
    
    query = db.query(SplashAd)
    
    # 状态筛选
    if status:
        query = query.filter(SplashAd.status == status)
    
    # 类型筛选
    if ad_type:
        query = query.filter(SplashAd.ad_type == ad_type)
    
    # 搜索筛选
    if search:
        query = query.filter(
            or_(
                SplashAd.title.contains(search),
                SplashAd.description.contains(search)
            )
        )
    
    # 总数
    total = query.count()
    
    # 分页
    ads = query.order_by(SplashAd.priority.desc(), SplashAd.created_at.desc())\
               .offset((page - 1) * page_size)\
               .limit(page_size)\
               .all()
    
    return SplashAdListResponse(
        items=ads,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )

@router.get("/splash-ads/{ad_id}", response_model=SplashAdResponse, summary="获取启动广告详情")
async def get_splash_ad(
    ad_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user_simple)
):
    """获取启动广告详情"""
    
    ad = db.query(SplashAd).filter(SplashAd.id == ad_id).first()
    if not ad:
        raise HTTPException(status_code=404, detail="广告不存在")
    
    return ad

@router.put("/splash-ads/{ad_id}", response_model=SplashAdResponse, summary="更新启动广告")
async def update_splash_ad(
    ad_id: int,
    ad_data: SplashAdUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user_simple)
):
    """更新启动广告"""
    
    ad = db.query(SplashAd).filter(SplashAd.id == ad_id).first()
    if not ad:
        raise HTTPException(status_code=404, detail="广告不存在")
    
    # 更新字段
    update_data = ad_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ad, field, value)
    
    ad.updated_at = datetime.now()
    
    db.commit()
    db.refresh(ad)
    
    return ad

@router.delete("/splash-ads/{ad_id}", summary="删除启动广告")
async def delete_splash_ad(
    ad_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user_simple)
):
    """删除启动广告"""
    
    ad = db.query(SplashAd).filter(SplashAd.id == ad_id).first()
    if not ad:
        raise HTTPException(status_code=404, detail="广告不存在")
    
    db.delete(ad)
    db.commit()
    
    return {"message": "广告删除成功"}

@router.post("/splash-ads/{ad_id}/status", response_model=SplashAdResponse, summary="更新广告状态")
async def update_ad_status(
    ad_id: int,
    status: AdStatus,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user_simple)
):
    """更新广告状态"""
    
    ad = db.query(SplashAd).filter(SplashAd.id == ad_id).first()
    if not ad:
        raise HTTPException(status_code=404, detail="广告不存在")
    
    ad.status = status
    ad.updated_at = datetime.now()
    
    db.commit()
    db.refresh(ad)
    
    return ad

@router.post("/splash-ads/upload", summary="上传广告素材")
async def upload_ad_media(
    file: UploadFile = File(...),
    current_user = Depends(get_admin_user_simple)
):
    """上传广告图片或视频"""
    
    # 检查文件类型
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mov', '.avi'}
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"不支持的文件类型，支持的格式: {', '.join(allowed_extensions)}"
        )
    
    # 检查文件大小（10MB限制）
    max_size = 10 * 1024 * 1024  # 10MB
    file_content = await file.read()
    if len(file_content) > max_size:
        raise HTTPException(status_code=400, detail="文件大小不能超过10MB")
    
    # 生成唯一文件名
    unique_filename = f"splash_ad_{uuid.uuid4().hex}{file_extension}"
    
    # 创建上传目录
    upload_dir = "static/uploads/splash_ads"
    os.makedirs(upload_dir, exist_ok=True)
    
    # 保存文件
    file_path = os.path.join(upload_dir, unique_filename)
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # 返回文件URL
    file_url = f"/static/uploads/splash_ads/{unique_filename}"
    
    return {
        "filename": unique_filename,
        "url": file_url,
        "size": len(file_content),
        "type": "image" if file_extension in {'.jpg', '.jpeg', '.png', '.gif'} else "video"
    }

# 客户端API（不需要管理员权限）
@router.get("/app/splash-ad", response_model=Optional[SplashAdClientResponse], summary="获取启动广告（客户端）")
async def get_app_splash_ad(
    db: Session = Depends(get_db)
):
    """获取当前有效的启动广告（供App使用）"""
    
    now = datetime.now()
    
    # 查询当前有效的广告
    query = db.query(SplashAd).filter(
        and_(
            SplashAd.status == AdStatus.ACTIVE,
            or_(SplashAd.start_time.is_(None), SplashAd.start_time <= now),
            or_(SplashAd.end_time.is_(None), SplashAd.end_time > now)
        )
    )
    
    # 按优先级和权重排序，获取一个广告
    ads = query.order_by(SplashAd.priority.desc()).all()
    
    if not ads:
        return None
    
    # 如果有多个相同优先级的广告，按权重随机选择
    import random
    
    # 按优先级分组
    priority_groups = {}
    for ad in ads:
        if ad.priority not in priority_groups:
            priority_groups[ad.priority] = []
        priority_groups[ad.priority].append(ad)
    
    # 选择最高优先级的组
    highest_priority = max(priority_groups.keys())
    highest_priority_ads = priority_groups[highest_priority]
    
    # 按权重随机选择
    weights = [ad.weight for ad in highest_priority_ads]
    selected_ad = random.choices(highest_priority_ads, weights=weights)[0]
    
    return SplashAdClientResponse(
        id=selected_ad.id,
        ad_type=selected_ad.ad_type.value,
        image_url=selected_ad.image_url,
        video_url=selected_ad.video_url,
        click_action=selected_ad.click_action,
        target_url=selected_ad.target_url,
        target_id=selected_ad.target_id,
        display_duration=selected_ad.display_duration,
        skip_enabled=selected_ad.skip_enabled,
        skip_delay=selected_ad.skip_delay
    )

@router.post("/app/splash-ad/{ad_id}/stats", summary="更新广告统计（客户端）")
async def update_ad_stats(
    ad_id: int,
    stats_data: SplashAdStatsUpdate,
    db: Session = Depends(get_db)
):
    """更新广告统计数据（供App使用）"""
    
    ad = db.query(SplashAd).filter(SplashAd.id == ad_id).first()
    if not ad:
        raise HTTPException(status_code=404, detail="广告不存在")
    
    if stats_data.action == "view":
        ad.view_count = (ad.view_count or 0) + 1
    elif stats_data.action == "click":
        ad.click_count = (ad.click_count or 0) + 1
    else:
        raise HTTPException(status_code=400, detail="无效的操作类型")
    
    ad.updated_at = datetime.now()
    
    db.commit()
    
    return {"message": "统计更新成功"}
