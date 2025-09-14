from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
import uuid
from fastapi import UploadFile

from ..models.message import Conversation, Message
from ..models.user import User
from ..schemas.chat import (
    MessageCreate, MessageResponse, ConversationResponse, 
    ConversationListResponse, MessageListResponse, ProductConsultRequest
)


class ChatService:
    
    def _get_message_type_int(self, message_type: str) -> int:
        """将字符串消息类型转换为整数"""
        type_mapping = {
            'text': 1,
            'image': 2,
            'product': 3,
            'system': 4
        }
        return type_mapping.get(message_type, 1)
    
    def _get_message_type_str(self, message_type: int) -> str:
        """将整数消息类型转换为字符串"""
        type_mapping = {
            1: 'text',
            2: 'image',
            3: 'product',
            4: 'system'
        }
        return type_mapping.get(message_type, 'text')
    
    async def get_or_create_conversation(self, db: Session, user1_id: int, user2_id: int) -> Conversation:
        """获取或创建对话"""
        # 确保user1_id < user2_id 以避免重复对话
        if user1_id > user2_id:
            user1_id, user2_id = user2_id, user1_id
        
        # 查找现有对话
        conversation = db.query(Conversation).filter(
            and_(
                Conversation.user1_id == user1_id,
                Conversation.user2_id == user2_id,
                or_(
                    Conversation.user1_deleted == False,
                    Conversation.user2_deleted == False
                )
            )
        ).first()
        
        if not conversation:
            # 创建新对话
            conversation = Conversation(
                user1_id=user1_id,
                user2_id=user2_id
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
        
        return conversation
    
    async def get_conversation(self, db: Session, conversation_id: int, user_id: int) -> Optional[ConversationResponse]:
        """获取对话详情"""
        conversation = db.query(Conversation).filter(
            and_(
                Conversation.id == conversation_id,
                or_(
                    Conversation.user1_id == user_id,
                    Conversation.user2_id == user_id
                )
            )
        ).first()
        
        if not conversation:
            return None
        
        # 获取对方用户信息
        other_user_id = conversation.user2_id if conversation.user1_id == user_id else conversation.user1_id
        other_user = db.query(User).filter(User.id == other_user_id).first()
        
        # 获取未读数量
        unread_count = conversation.user1_unread_count if conversation.user1_id == user_id else conversation.user2_unread_count
        
        return ConversationResponse(
            id=conversation.id,
            user1_id=conversation.user1_id,
            user2_id=conversation.user2_id,
            last_message_id=conversation.last_message_id,
            last_message_time=conversation.last_message_time,
            user1_unread_count=conversation.user1_unread_count,
            user2_unread_count=conversation.user2_unread_count,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            other_user={
                "id": other_user.id,
                "nickname": other_user.nickname,
                "avatar": other_user.avatar_url
            } if other_user else None,
            unread_count=unread_count
        )
    
    async def get_user_conversations(self, db: Session, user_id: int, page: int = 1, page_size: int = 20) -> ConversationListResponse:
        """获取用户的对话列表"""
        query = db.query(Conversation).filter(
            and_(
                or_(
                    Conversation.user1_id == user_id,
                    Conversation.user2_id == user_id
                ),
                # 排除已删除的对话
                or_(
                    and_(Conversation.user1_id == user_id, Conversation.user1_deleted == False),
                    and_(Conversation.user2_id == user_id, Conversation.user2_deleted == False)
                )
            )
        ).order_by(desc(Conversation.last_message_time))
        
        total = query.count()
        conversations = query.offset((page - 1) * page_size).limit(page_size).all()
        
        # 转换为响应格式
        conversation_list = []
        for conversation in conversations:
            # 获取对方用户信息
            other_user_id = conversation.user2_id if conversation.user1_id == user_id else conversation.user1_id
            other_user = db.query(User).filter(User.id == other_user_id).first()
            
            # 获取最后一条消息
            last_message = None
            if conversation.last_message_id:
                message = db.query(Message).filter(Message.id == conversation.last_message_id).first()
                if message:
                    last_message = MessageResponse(
                        id=message.id,
                        conversation_id=message.conversation_id,
                        sender_id=message.sender_id,
                        receiver_id=message.receiver_id,
                        message_type=self._get_message_type_str(message.message_type),
                        content=message.content,
                        related_id=message.related_id,
                        is_read=message.is_read,
                        created_at=message.created_at,
                        updated_at=message.updated_at
                    )
            
            # 获取未读数量
            unread_count = conversation.user1_unread_count if conversation.user1_id == user_id else conversation.user2_unread_count
            
            conversation_response = ConversationResponse(
                id=conversation.id,
                user1_id=conversation.user1_id,
                user2_id=conversation.user2_id,
                last_message_id=conversation.last_message_id,
                last_message_time=conversation.last_message_time,
                user1_unread_count=conversation.user1_unread_count,
                user2_unread_count=conversation.user2_unread_count,
                created_at=conversation.created_at,
                updated_at=conversation.updated_at,
                other_user={
                    "id": other_user.id,
                    "nickname": other_user.nickname,
                    "avatar": other_user.avatar_url
                } if other_user else None,
                last_message=last_message,
                unread_count=unread_count
            )
            conversation_list.append(conversation_response)
        
        return ConversationListResponse(
            items=conversation_list,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )
    
    async def send_message(
        self, 
        db: Session, 
        sender_id: int, 
        receiver_id: int, 
        content: str,
        message_type: str = "text",
        conversation_id: Optional[int] = None,
        related_id: Optional[int] = None
    ) -> MessageResponse:
        """发送消息"""
        
        # 获取或创建对话
        if conversation_id:
            conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
            if not conversation:
                raise ValueError("对话不存在")
        else:
            conversation = await self.get_or_create_conversation(db, sender_id, receiver_id)
        
        # 转换消息类型为整数
        message_type_int = self._get_message_type_int(message_type)
        
        # 创建消息
        message = Message(
            conversation_id=conversation.id,
            sender_id=sender_id,
            receiver_id=receiver_id,
            message_type=message_type_int,
            content=content,
            related_id=related_id
        )
        
        db.add(message)
        db.flush()  # 获取message.id
        
        # 更新对话信息
        conversation.last_message_id = message.id
        conversation.last_message_time = message.created_at
        
        # 更新未读数量
        if conversation.user1_id == receiver_id:
            conversation.user1_unread_count += 1
        else:
            conversation.user2_unread_count += 1
        
        db.commit()
        db.refresh(message)
        
        # 获取发送者信息
        sender = db.query(User).filter(User.id == sender_id).first()
        
        return MessageResponse(
            id=message.id,
            conversation_id=message.conversation_id,
            sender_id=message.sender_id,
            receiver_id=message.receiver_id,
            message_type=self._get_message_type_str(message.message_type),
            content=message.content,
            related_id=message.related_id,
            is_read=message.is_read,
            created_at=message.created_at,
            updated_at=message.updated_at,
            sender_info={
                "id": sender.id,
                "nickname": sender.nickname,
                "avatar": sender.avatar_url
            } if sender else None
        )
    
    async def get_conversation_messages(
        self, 
        db: Session, 
        conversation_id: int, 
        user_id: int, 
        page: int = 1, 
        page_size: int = 50
    ) -> MessageListResponse:
        """获取对话消息列表"""
        
        # 验证对话权限
        conversation = db.query(Conversation).filter(
            and_(
                Conversation.id == conversation_id,
                or_(
                    Conversation.user1_id == user_id,
                    Conversation.user2_id == user_id
                )
            )
        ).first()
        
        if not conversation:
            raise ValueError("对话不存在或无权限")
        
        # 查询消息
        query = db.query(Message).filter(
            and_(
                Message.conversation_id == conversation_id,
                Message.is_deleted == False
            )
        ).order_by(desc(Message.created_at))
        
        total = query.count()
        messages = query.offset((page - 1) * page_size).limit(page_size).all()
        
        # 转换为响应格式
        message_list = []
        for message in messages:
            sender = db.query(User).filter(User.id == message.sender_id).first()
            message_response = MessageResponse(
                id=message.id,
                conversation_id=message.conversation_id,
                sender_id=message.sender_id,
                receiver_id=message.receiver_id,
                message_type=self._get_message_type_str(message.message_type),
                content=message.content,
                related_id=message.related_id,
                is_read=message.is_read,
                created_at=message.created_at,
                updated_at=message.updated_at,
                sender_info={
                    "id": sender.id,
                    "nickname": sender.nickname,
                    "avatar": sender.avatar_url
                } if sender else None
            )
            message_list.append(message_response)
        
        return MessageListResponse(
            items=message_list,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )
    
    async def mark_messages_as_read(self, db: Session, conversation_id: int, user_id: int) -> bool:
        """标记对话中的消息为已读"""
        conversation = db.query(Conversation).filter(
            and_(
                Conversation.id == conversation_id,
                or_(
                    Conversation.user1_id == user_id,
                    Conversation.user2_id == user_id
                )
            )
        ).first()
        
        if not conversation:
            return False
        
        # 标记未读消息为已读
        db.query(Message).filter(
            and_(
                Message.conversation_id == conversation_id,
                Message.receiver_id == user_id,
                Message.is_read == False
            )
        ).update({"is_read": True})
        
        # 重置未读数量
        if conversation.user1_id == user_id:
            conversation.user1_unread_count = 0
        else:
            conversation.user2_unread_count = 0
        
        db.commit()
        return True
    
    async def mark_message_as_read(self, db: Session, message_id: int, user_id: int) -> bool:
        """标记单条消息为已读"""
        message = db.query(Message).filter(
            and_(
                Message.id == message_id,
                Message.receiver_id == user_id,
                Message.is_read == False
            )
        ).first()
        
        if not message:
            return False
        
        message.is_read = True
        
        # 更新对话未读数量
        conversation = db.query(Conversation).filter(Conversation.id == message.conversation_id).first()
        if conversation:
            if conversation.user1_id == user_id and conversation.user1_unread_count > 0:
                conversation.user1_unread_count -= 1
            elif conversation.user2_id == user_id and conversation.user2_unread_count > 0:
                conversation.user2_unread_count -= 1
        
        db.commit()
        return True
    
    async def get_unread_message_count(self, db: Session, user_id: int) -> int:
        """获取用户未读消息总数"""
        count = db.query(func.sum(
            case(
                (Conversation.user1_id == user_id, Conversation.user1_unread_count),
                (Conversation.user2_id == user_id, Conversation.user2_unread_count),
                else_=0
            )
        )).filter(
            or_(
                Conversation.user1_id == user_id,
                Conversation.user2_id == user_id
            )
        ).scalar() or 0
        
        return int(count)
    
    async def delete_conversation(self, db: Session, conversation_id: int, user_id: int) -> bool:
        """删除对话（软删除）"""
        conversation = db.query(Conversation).filter(
            and_(
                Conversation.id == conversation_id,
                or_(
                    Conversation.user1_id == user_id,
                    Conversation.user2_id == user_id
                )
            )
        ).first()
        
        if not conversation:
            return False
        
        # 标记为删除
        if conversation.user1_id == user_id:
            conversation.user1_deleted = True
            conversation.user1_unread_count = 0
        else:
            conversation.user2_deleted = True
            conversation.user2_unread_count = 0
        
        db.commit()
        return True
    
    async def delete_message(self, db: Session, message_id: int, user_id: int) -> bool:
        """删除消息（软删除，仅发送者可删除）"""
        message = db.query(Message).filter(
            and_(
                Message.id == message_id,
                Message.sender_id == user_id,
                Message.is_deleted == False
            )
        ).first()
        
        if not message:
            return False
        
        message.is_deleted = True
        db.commit()
        return True
    
    async def search_messages(
        self, 
        db: Session, 
        user_id: int, 
        keyword: str, 
        conversation_id: Optional[int] = None,
        page: int = 1, 
        page_size: int = 20
    ) -> MessageListResponse:
        """搜索消息"""
        query = db.query(Message).join(Conversation).filter(
            and_(
                or_(
                    Conversation.user1_id == user_id,
                    Conversation.user2_id == user_id
                ),
                Message.content.contains(keyword),
                Message.is_deleted == False
            )
        )
        
        if conversation_id:
            query = query.filter(Message.conversation_id == conversation_id)
        
        query = query.order_by(desc(Message.created_at))
        
        total = query.count()
        messages = query.offset((page - 1) * page_size).limit(page_size).all()
        
        # 转换为响应格式
        message_list = []
        for message in messages:
            sender = db.query(User).filter(User.id == message.sender_id).first()
            message_response = MessageResponse(
                id=message.id,
                conversation_id=message.conversation_id,
                sender_id=message.sender_id,
                receiver_id=message.receiver_id,
                message_type=self._get_message_type_str(message.message_type),
                content=message.content,
                related_id=message.related_id,
                is_read=message.is_read,
                created_at=message.created_at,
                updated_at=message.updated_at,
                sender_info={
                    "id": sender.id,
                    "nickname": sender.nickname,
                    "avatar": sender.avatar_url
                } if sender else None
            )
            message_list.append(message_response)
        
        return MessageListResponse(
            items=message_list,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )
    
    async def upload_chat_image(self, file: UploadFile, user_id: int) -> str:
        """上传聊天图片"""
        # 验证文件类型
        if not file.content_type.startswith('image/'):
            raise ValueError("只能上传图片文件")
        
        # 验证文件大小（5MB）
        if file.size > 5 * 1024 * 1024:
            raise ValueError("图片文件大小不能超过5MB")
        
        # 创建上传目录
        upload_dir = f"static/uploads/chat/{user_id}"
        os.makedirs(upload_dir, exist_ok=True)
        
        # 生成文件名
        file_extension = file.filename.split('.')[-1].lower()
        filename = f"{uuid.uuid4().hex}.{file_extension}"
        file_path = os.path.join(upload_dir, filename)
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 返回文件URL
        return f"/static/uploads/chat/{user_id}/{filename}"
    
    async def send_product_consultation(
        self, 
        db: Session, 
        user_id: int, 
        request: ProductConsultRequest
    ) -> MessageResponse:
        """发送商品咨询"""
        
        # 构造咨询消息内容
        content = f"我对您的商品感兴趣，想了解一下：{request.message}"
        
        # 发送消息
        message = await self.send_message(
            db=db,
            sender_id=user_id,
            receiver_id=request.seller_id,
            content=content,
            message_type="product",
            related_id=request.product_id
        )
        
        return message


# 从sqlalchemy导入case函数
from sqlalchemy import case
