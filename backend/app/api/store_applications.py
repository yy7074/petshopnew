from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
from datetime import datetime

from ..core.database import get_db
from ..core.security import get_current_user, get_admin_user
from ..models.user import User
from ..schemas.store_application import (
    StoreApplicationCreate, StoreApplicationUpdate, StoreApplicationResponse,
    StoreApplicationListResponse, StoreApplicationReview, StoreTypesResponse
)
from ..services.store_application_service import StoreApplicationService

router = APIRouter()
application_service = StoreApplicationService()

@router.get("/test-auth")
async def test_auth(current_user: User = Depends(get_current_user)):
    """测试用户认证"""
    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "phone": current_user.phone,
        "message": "认证成功"
    }

@router.get("/types", response_model=StoreTypesResponse)
async def get_store_types():
    """获取店铺类型列表"""
    return await application_service.get_store_types()

@router.post("/", response_model=StoreApplicationResponse)
async def create_application(
    application_data: StoreApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建店铺申请"""
    try:
        application = await application_service.create_application(
            db, application_data, current_user.id
        )
        return application
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/my", response_model=Optional[StoreApplicationResponse])
async def get_my_application(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取我的店铺申请"""
    try:
        application = await application_service.get_application_by_user(
            db, current_user.id
        )
        return application
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{application_id}", response_model=StoreApplicationResponse)
async def get_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取店铺申请详情"""
    try:
        application = await application_service.get_application_by_id(
            db, application_id
        )
        if not application:
            raise HTTPException(status_code=404, detail="申请不存在")
        
        # 检查权限：只有申请人或管理员可以查看
        if application.user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(status_code=403, detail="无权限访问")
        
        return application
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{application_id}", response_model=StoreApplicationResponse)
async def update_application(
    application_id: int,
    application_data: StoreApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新店铺申请"""
    try:
        application = await application_service.update_application(
            db, application_id, application_data, current_user.id
        )
        return application
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=StoreApplicationListResponse)
async def get_applications_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[int] = Query(None, ge=0, le=3),
    store_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """获取店铺申请列表（管理员）"""
    try:
        applications = await application_service.get_applications_list(
            db, page, page_size, status, store_type
        )
        return applications
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{application_id}/review", response_model=StoreApplicationResponse)
async def review_application(
    application_id: int,
    review_data: StoreApplicationReview,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """审核店铺申请（管理员）"""
    try:
        application = await application_service.review_application(
            db, application_id, review_data, current_user.id
        )
        return application
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{application_id}/create-store")
async def create_store_from_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """从申请创建店铺（支付完成后）"""
    try:
        result = await application_service.create_store_from_application(
            db, application_id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{application_id}/payment-completed", response_model=StoreApplicationResponse)
async def mark_payment_completed(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """标记支付完成"""
    try:
        application = await application_service.mark_payment_completed(
            db, application_id
        )
        return application
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """上传申请相关图片"""
    try:
        print(f"上传文件: {file.filename}, 类型: {file.content_type}, 用户: {current_user.id}")
        
        # 检查文件类型
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png']
        if file.content_type not in allowed_types:
            print(f"不支持的文件类型: {file.content_type}")
            raise HTTPException(status_code=400, detail="只支持JPG、PNG格式的图片")
        
        # 检查文件大小（5MB）
        file_size = 0
        content = await file.read()
        file_size = len(content)
        if file_size > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="图片大小不能超过5MB")
        
        # 生成文件名
        file_extension = file.filename.split('.')[-1] if file.filename else 'jpg'
        filename = f"store_application_{current_user.id}_{uuid.uuid4().hex}.{file_extension}"
        
        # 确保上传目录存在
        upload_dir = "static/uploads/store_applications"
        os.makedirs(upload_dir, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(upload_dir, filename)
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        # 返回文件URL
        file_url = f"/static/uploads/store_applications/{filename}"
        
        return {
            "url": file_url,
            "filename": filename,
            "size": file_size
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")
