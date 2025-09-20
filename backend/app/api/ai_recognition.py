from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
import base64

from ..core.database import get_db
from ..core.security import get_current_user, get_admin_user
from ..models.user import User
from ..services.ai_recognition_service import AIRecognitionService
from ..schemas.ai_recognition import (
    RecognitionRequest, RecognitionResponse, 
    RecognitionHistoryResponse, RecognitionStatsResponse,
    BreedEncyclopediaResponse
)

router = APIRouter(prefix="/ai-recognition", tags=["AI识别"])

@router.post("/recognize", response_model=RecognitionResponse)
async def recognize_pet_image(
    request: RecognitionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """识别宠物图片"""
    try:
        # 验证请求参数
        if not request.image_data and not request.image_url:
            raise HTTPException(status_code=400, detail="必须提供image_data或image_url其中之一")
        
        ai_service = AIRecognitionService()
        result = await ai_service.recognize_pet_image(
            db=db,
            user_id=current_user.id,
            image_data=request.image_data,
            image_format=request.image_format,
            image_url=request.image_url
        )
        
        return RecognitionResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"识别失败: {str(e)}")

@router.post("/recognize-upload")
async def recognize_uploaded_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """上传图片进行识别"""
    try:
        # 验证文件类型
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="请上传图片文件")
        
        # 读取文件内容
        content = await file.read()
        
        # 转换为base64
        image_data = base64.b64encode(content).decode('utf-8')
        
        # 提取文件格式
        image_format = file.filename.split('.')[-1].lower() if file.filename else 'jpg'
        
        ai_service = AIRecognitionService()
        result = await ai_service.recognize_pet_image(
            db=db,
            user_id=current_user.id,
            image_data=image_data,
            image_format=image_format
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"图片识别失败: {str(e)}")

@router.get("/history", response_model=RecognitionHistoryResponse)
async def get_recognition_history(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户识别历史"""
    try:
        ai_service = AIRecognitionService()
        result = await ai_service.get_recognition_history(
            db=db,
            user_id=current_user.id,
            page=page,
            page_size=page_size
        )
        
        return RecognitionHistoryResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史记录失败: {str(e)}")

@router.get("/user-stats")
async def get_user_recognition_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户识别统计"""
    try:
        from ..models.ai_recognition import AIRecognitionRecord
        from sqlalchemy import func
        from datetime import datetime, timedelta
        
        # 用户总识别次数
        total_recognitions = db.query(func.count(AIRecognitionRecord.id)).filter(
            AIRecognitionRecord.user_id == current_user.id
        ).scalar() or 0
        
        # 最近30天识别次数
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_recognitions = db.query(func.count(AIRecognitionRecord.id)).filter(
            AIRecognitionRecord.user_id == current_user.id,
            AIRecognitionRecord.created_at >= thirty_days_ago
        ).scalar() or 0
        
        # 平均置信度
        avg_confidence = db.query(func.avg(AIRecognitionRecord.confidence)).filter(
            AIRecognitionRecord.user_id == current_user.id
        ).scalar() or 0.0
        
        # 最常识别的宠物类型
        most_common_type = db.query(
            AIRecognitionRecord.pet_type,
            func.count(AIRecognitionRecord.id).label('count')
        ).filter(
            AIRecognitionRecord.user_id == current_user.id
        ).group_by(AIRecognitionRecord.pet_type).order_by(
            func.count(AIRecognitionRecord.id).desc()
        ).first()
        
        # 检查今日剩余次数
        ai_service = AIRecognitionService()
        daily_check = await ai_service._check_daily_limit(db, current_user.id)
        
        return {
            "total_recognitions": total_recognitions,
            "recent_recognitions": recent_recognitions,
            "avg_confidence": round(float(avg_confidence), 3),
            "most_common_type": most_common_type.pet_type if most_common_type else None,
            "most_common_count": most_common_type.count if most_common_type else 0,
            "daily_remaining": daily_check.get("remaining", 0),
            "daily_limit": ai_service.RECOGNITION_CONFIG["max_daily_recognitions"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")

@router.get("/encyclopedia", response_model=BreedEncyclopediaResponse)
async def get_breed_encyclopedia(
    pet_type: Optional[str] = None
):
    """获取品种百科"""
    try:
        ai_service = AIRecognitionService()
        result = await ai_service.get_breed_encyclopedia(pet_type)
        
        return BreedEncyclopediaResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取品种百科失败: {str(e)}")

@router.post("/feedback")
async def submit_recognition_feedback(
    recognition_id: int,
    feedback_type: str,
    correct_breed: Optional[str] = None,
    comments: Optional[str] = None,
    rating: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """提交识别结果反馈"""
    try:
        from ..models.ai_recognition import AIRecognitionFeedback, AIRecognitionRecord
        
        # 验证识别记录存在且属于当前用户
        recognition = db.query(AIRecognitionRecord).filter(
            AIRecognitionRecord.id == recognition_id,
            AIRecognitionRecord.user_id == current_user.id
        ).first()
        
        if not recognition:
            raise HTTPException(status_code=404, detail="识别记录不存在")
        
        # 验证反馈类型
        valid_types = ["correct", "incorrect", "partial"]
        if feedback_type not in valid_types:
            raise HTTPException(status_code=400, detail=f"无效的反馈类型，支持: {', '.join(valid_types)}")
        
        # 验证评分
        if rating is not None and (rating < 1 or rating > 5):
            raise HTTPException(status_code=400, detail="评分必须在1-5之间")
        
        # 检查是否已经提交过反馈
        existing_feedback = db.query(AIRecognitionFeedback).filter(
            AIRecognitionFeedback.recognition_id == recognition_id,
            AIRecognitionFeedback.user_id == current_user.id
        ).first()
        
        if existing_feedback:
            # 更新现有反馈
            existing_feedback.feedback_type = feedback_type
            existing_feedback.correct_breed = correct_breed
            existing_feedback.comments = comments
            existing_feedback.rating = rating
        else:
            # 创建新反馈
            feedback = AIRecognitionFeedback(
                recognition_id=recognition_id,
                user_id=current_user.id,
                feedback_type=feedback_type,
                correct_breed=correct_breed,
                comments=comments,
                rating=rating
            )
            db.add(feedback)
        
        db.commit()
        
        return {
            "success": True,
            "message": "反馈提交成功，感谢您的反馈！"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"提交反馈失败: {str(e)}")

# 管理员接口
@router.get("/admin/statistics", response_model=RecognitionStatsResponse)
async def get_admin_recognition_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """获取识别统计信息（管理员）"""
    try:
        ai_service = AIRecognitionService()
        result = await ai_service.get_recognition_statistics(db)
        
        return RecognitionStatsResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")

@router.get("/admin/feedback")
async def get_recognition_feedback(
    page: int = 1,
    page_size: int = 20,
    feedback_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """获取用户反馈（管理员）"""
    try:
        from ..models.ai_recognition import AIRecognitionFeedback
        from sqlalchemy import and_
        
        query = db.query(AIRecognitionFeedback)
        
        if feedback_type:
            query = query.filter(AIRecognitionFeedback.feedback_type == feedback_type)
        
        query = query.order_by(AIRecognitionFeedback.created_at.desc())
        
        total = query.count()
        feedbacks = query.offset((page - 1) * page_size).limit(page_size).all()
        
        feedback_items = []
        for feedback in feedbacks:
            feedback_items.append({
                "id": feedback.id,
                "recognition_id": feedback.recognition_id,
                "user_id": feedback.user_id,
                "feedback_type": feedback.feedback_type,
                "correct_breed": feedback.correct_breed,
                "comments": feedback.comments,
                "rating": feedback.rating,
                "created_at": feedback.created_at.isoformat()
            })
        
        return {
            "items": feedback_items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取反馈失败: {str(e)}")

@router.post("/test")
async def test_recognition_api(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """测试AI识别API"""
    try:
        # 使用一个测试图片URL
        test_image_url = "https://picsum.photos/400/400?random=1"
        
        ai_service = AIRecognitionService()
        result = await ai_service.recognize_pet_image(
            db=db,
            user_id=current_user.id,
            image_url=test_image_url
        )
        
        return {
            "success": True,
            "message": "测试完成",
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"测试失败: {str(e)}")

@router.get("/config")
async def get_recognition_config():
    """获取识别配置信息"""
    try:
        ai_service = AIRecognitionService()
        config = ai_service.RECOGNITION_CONFIG.copy()
        
        return {
            "success": True,
            "data": {
                "config": config,
                "supported_pet_types": ["dog", "cat", "bird", "fish"],
                "description": {
                    "max_image_size": "最大图片大小（字节）",
                    "min_image_size": "最小图片大小（字节）",
                    "supported_formats": "支持的图片格式",
                    "max_daily_recognitions": "每日最大识别次数",
                    "confidence_threshold": "置信度阈值",
                    "cache_duration_hours": "缓存持续时间（小时）"
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取配置失败: {str(e)}")

@router.post("/admin/update-breed-info")
async def update_breed_info(
    pet_type: str,
    breed_key: str,
    breed_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """更新品种信息（管理员）"""
    try:
        from ..models.ai_recognition import PetBreedInfo
        
        # 查找或创建品种信息
        breed_info = db.query(PetBreedInfo).filter(
            PetBreedInfo.pet_type == pet_type,
            PetBreedInfo.breed_key == breed_key
        ).first()
        
        if not breed_info:
            breed_info = PetBreedInfo(
                pet_type=pet_type,
                breed_key=breed_key
            )
            db.add(breed_info)
        
        # 更新字段
        for field, value in breed_data.items():
            if hasattr(breed_info, field):
                setattr(breed_info, field, value)
        
        breed_info.is_verified = True
        
        db.commit()
        db.refresh(breed_info)
        
        return {
            "success": True,
            "message": "品种信息更新成功",
            "breed_id": breed_info.id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新品种信息失败: {str(e)}")