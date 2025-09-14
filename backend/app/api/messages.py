from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..schemas.message import (
    MessageCreate, MessageResponse, MessageListResponse,
    ConversationResponse, ConversationListResponse,
    SystemNotificationCreate, SystemNotificationResponse, SystemNotificationListResponse,
    UserNotificationUpdate, MessageStats, SendMessageRequest,
    MarkReadRequest, DeleteMessageRequest, CreateNotificationRequest
)
from ..services.message_service import MessageService

router = APIRouter()
message_service = MessageService()


# 对话相关接口
@router.get("/conversations", response_model=ConversationListResponse)
async def get_conversations(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户对话列表"""
    result = await message_service.get_conversations(db, current_user.id, page, page_size)
    return ConversationListResponse(**result)


@router.get("/conversations/{other_user_id}", response_model=ConversationResponse)
async def get_or_create_conversation(
    other_user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取或创建与指定用户的对话"""
    if other_user_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能与自己创建对话")
    
    return await message_service.get_or_create_conversation(db, current_user.id, other_user_id)


@router.get("/conversations/{conversation_id}/messages", response_model=MessageListResponse)
async def get_messages(
    conversation_id: int,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取对话消息列表"""
    result = await message_service.get_messages(db, conversation_id, current_user.id, page, page_size)
    return MessageListResponse(**result)


@router.post("/conversations/{conversation_id}/read")
async def mark_messages_read(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """标记对话消息为已读"""
    return await message_service.mark_messages_read(db, conversation_id, current_user.id)


# 消息相关接口
@router.post("/send", response_model=MessageResponse)
async def send_message(
    message_data: SendMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """发送消息"""
    if message_data.receiver_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能给自己发送消息")
    
    return await message_service.send_message(db, current_user.id, message_data)


# 系统通知相关接口
@router.get("/notifications", response_model=SystemNotificationListResponse)
async def get_user_notifications(
    notification_type: Optional[str] = Query(None, description="通知类型"),
    is_read: Optional[bool] = Query(None, description="是否已读"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户通知列表"""
    result = await message_service.get_user_notifications(
        db, current_user.id, notification_type, is_read, page, page_size
    )
    return SystemNotificationListResponse(**result)


@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """标记通知为已读"""
    return await message_service.mark_notification_read(db, current_user.id, notification_id)


@router.get("/stats", response_model=MessageStats)
async def get_message_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取消息统计"""
    return await message_service.get_message_stats(db, current_user.id)


# 管理员接口
@router.post("/admin/notifications", response_model=SystemNotificationResponse)
async def create_system_notification(
    notification_data: CreateNotificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建系统通知（管理员）"""
    # 这里应该检查管理员权限，简化处理
    if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    return await message_service.create_system_notification(db, notification_data)


# 获取消息类型
@router.get("/types")
async def get_message_types():
    """获取消息类型列表"""
    return {
        "message_types": [
            {"key": "text", "name": "文本消息"},
            {"key": "image", "name": "图片消息"},
            {"key": "product", "name": "商品消息"},
            {"key": "system", "name": "系统消息"}
        ],
        "notification_types": [
            {"key": "system", "name": "系统通知"},
            {"key": "auction", "name": "拍卖通知"},
            {"key": "order", "name": "订单通知"},
            {"key": "payment", "name": "支付通知"}
        ]
    }


# 快速回复模板
@router.get("/quick-replies")
async def get_quick_replies():
    """获取快速回复模板"""
    return {
        "items": [
            {"text": "您好，请问有什么可以帮助您的吗？"},
            {"text": "商品还在吗？"},
            {"text": "价格可以商量吗？"},
            {"text": "什么时候可以发货？"},
            {"text": "支持同城自提吗？"},
            {"text": "可以看看实物吗？"},
            {"text": "谢谢，我再考虑一下"},
            {"text": "好的，我们成交"}
        ]
    }
