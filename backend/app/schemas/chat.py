from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)
    message_type: str = Field(default="text", pattern="^(text|image|product|system)$")
    related_id: Optional[int] = None


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    sender_id: int
    receiver_id: int
    message_type: str
    content: str
    related_id: Optional[int] = None
    is_read: bool
    created_at: datetime
    updated_at: datetime
    
    # 发送者信息
    sender_info: Optional[dict] = None
    
    class Config:
        from_attributes = True


class MessageListResponse(BaseModel):
    items: List[MessageResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ConversationResponse(BaseModel):
    id: int
    user1_id: int
    user2_id: int
    last_message_id: Optional[int] = None
    last_message_time: Optional[datetime] = None
    user1_unread_count: int = 0
    user2_unread_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    # 对方用户信息
    other_user: Optional[dict] = None
    # 最后一条消息
    last_message: Optional[MessageResponse] = None
    # 当前用户的未读数量
    unread_count: int = 0
    
    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    items: List[ConversationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ConversationCreate(BaseModel):
    other_user_id: int = Field(..., gt=0)
    initial_message: Optional[str] = None


class ChatUserInfo(BaseModel):
    id: int
    nickname: str
    avatar: Optional[str] = None
    is_online: bool = False


class WebSocketMessage(BaseModel):
    type: str  # message, typing, read
    conversation_id: Optional[int] = None
    receiver_id: Optional[int] = None
    content: Optional[str] = None
    message_type: str = "text"
    is_typing: bool = False


class ProductConsultRequest(BaseModel):
    """商品咨询请求"""
    product_id: int = Field(..., gt=0)
    seller_id: int = Field(..., gt=0)
    message: str = Field(..., min_length=1, max_length=500)
    
    
class ConsultationResponse(BaseModel):
    """咨询响应"""
    conversation_id: int
    message_id: int
    message: str = "咨询消息发送成功"
