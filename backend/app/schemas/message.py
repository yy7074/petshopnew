from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


# 对话相关schemas
class ConversationBase(BaseModel):
    pass


class ConversationResponse(ConversationBase):
    id: int
    user1_id: int
    user2_id: int
    last_message_id: Optional[int] = None
    last_message_time: Optional[datetime] = None
    user1_unread_count: int
    user2_unread_count: int
    created_at: datetime
    updated_at: datetime
    
    # 扩展字段
    other_user_info: Optional[Dict[str, Any]] = None
    last_message_content: Optional[str] = None
    unread_count: Optional[int] = None  # 当前用户的未读数

    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    items: List[ConversationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# 消息相关schemas
class MessageBase(BaseModel):
    content: str
    message_type: Optional[str] = "text"
    related_id: Optional[int] = None


class MessageCreate(MessageBase):
    receiver_id: int


class MessageResponse(MessageBase):
    id: int
    conversation_id: int
    sender_id: int
    receiver_id: int
    is_read: bool
    is_deleted: bool
    created_at: datetime
    
    # 扩展字段
    sender_info: Optional[Dict[str, Any]] = None
    receiver_info: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class MessageListResponse(BaseModel):
    items: List[MessageResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# 系统通知相关schemas
class SystemNotificationBase(BaseModel):
    title: str
    content: str
    notification_type: str
    target_type: Optional[str] = "all"
    target_ids: Optional[List[int]] = None
    related_type: Optional[str] = None
    related_id: Optional[int] = None
    extra_data: Optional[Dict[str, Any]] = None
    priority: Optional[int] = 0
    publish_time: Optional[datetime] = None
    expire_time: Optional[datetime] = None


class SystemNotificationCreate(SystemNotificationBase):
    pass


class SystemNotificationUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None
    publish_time: Optional[datetime] = None
    expire_time: Optional[datetime] = None


class SystemNotificationResponse(SystemNotificationBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    # 用户相关字段
    is_read: Optional[bool] = None
    read_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class SystemNotificationListResponse(BaseModel):
    items: List[SystemNotificationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# 用户通知状态schemas
class UserNotificationUpdate(BaseModel):
    is_read: Optional[bool] = None
    is_deleted: Optional[bool] = None


class UserNotificationResponse(BaseModel):
    id: int
    user_id: int
    notification_id: int
    is_read: bool
    is_deleted: bool
    read_time: Optional[datetime] = None
    created_at: datetime
    
    # 通知详情
    notification: Optional[SystemNotificationResponse] = None

    class Config:
        from_attributes = True


# 消息统计schemas
class MessageStats(BaseModel):
    total_conversations: int
    unread_conversations: int
    total_unread_messages: int
    system_notifications: int
    unread_notifications: int


# 发送消息请求
class SendMessageRequest(BaseModel):
    receiver_id: int
    content: str
    message_type: Optional[str] = "text"
    related_id: Optional[int] = None


# 标记消息已读请求
class MarkReadRequest(BaseModel):
    message_ids: List[int]


# 删除消息请求  
class DeleteMessageRequest(BaseModel):
    message_ids: List[int]


# 创建系统通知请求
class CreateNotificationRequest(SystemNotificationBase):
    pass


# 批量操作通知请求
class BatchNotificationRequest(BaseModel):
    notification_ids: List[int]
    action: str  # read, delete, restore
