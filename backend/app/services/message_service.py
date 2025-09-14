from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import HTTPException

from ..models.message import Conversation, Message
from ..models.notification import SystemNotification, UserNotification, MessageTemplate
from ..models.user import User
from ..schemas.message import (
    MessageCreate, MessageResponse, MessageListResponse,
    ConversationResponse, ConversationListResponse,
    SystemNotificationCreate, SystemNotificationResponse, SystemNotificationListResponse,
    UserNotificationUpdate, MessageStats, SendMessageRequest
)


class MessageService:
    
    def __init__(self):
        pass

    # 对话相关方法
    async def get_conversations(
        self,
        db: Session,
        user_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """获取用户对话列表"""
        query = db.query(Conversation).filter(
            or_(
                and_(Conversation.user1_id == user_id, ~Conversation.user1_deleted),
                and_(Conversation.user2_id == user_id, ~Conversation.user2_deleted)
            )
        )
        
        # 总数
        total = query.count()
        
        # 分页
        offset = (page - 1) * page_size
        conversations = query.order_by(desc(Conversation.last_message_time)).offset(offset).limit(page_size).all()
        
        # 格式化响应
        items = []
        for conv in conversations:
            formatted_conv = await self._format_conversation_response(db, conv, user_id)
            items.append(formatted_conv)
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }

    async def get_or_create_conversation(
        self,
        db: Session,
        user1_id: int,
        user2_id: int
    ) -> ConversationResponse:
        """获取或创建对话"""
        # 查找现有对话
        conversation = db.query(Conversation).filter(
            or_(
                and_(Conversation.user1_id == user1_id, Conversation.user2_id == user2_id),
                and_(Conversation.user1_id == user2_id, Conversation.user2_id == user1_id)
            )
        ).first()
        
        if not conversation:
            # 创建新对话
            conversation = Conversation(
                user1_id=min(user1_id, user2_id),
                user2_id=max(user1_id, user2_id)
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
        
        return await self._format_conversation_response(db, conversation, user1_id)

    # 消息相关方法
    async def send_message(
        self,
        db: Session,
        sender_id: int,
        message_data: SendMessageRequest
    ) -> MessageResponse:
        """发送消息"""
        # 获取或创建对话
        conversation = await self.get_or_create_conversation(db, sender_id, message_data.receiver_id)
        
        # 创建消息
        message = Message(
            conversation_id=conversation.id,
            sender_id=sender_id,
            receiver_id=message_data.receiver_id,
            content=message_data.content,
            message_type=message_data.message_type,
            related_id=message_data.related_id
        )
        db.add(message)
        
        # 更新对话信息
        conv_obj = db.query(Conversation).filter(Conversation.id == conversation.id).first()
        conv_obj.last_message_id = message.id
        conv_obj.last_message_time = func.now()
        
        # 更新未读计数
        if conv_obj.user1_id == message_data.receiver_id:
            conv_obj.user1_unread_count += 1
        else:
            conv_obj.user2_unread_count += 1
        
        db.commit()
        db.refresh(message)
        
        return await self._format_message_response(db, message)

    async def get_messages(
        self,
        db: Session,
        conversation_id: int,
        user_id: int,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """获取对话消息列表"""
        # 验证用户是否有权限访问此对话
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            or_(Conversation.user1_id == user_id, Conversation.user2_id == user_id)
        ).first()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="对话不存在或无权限访问")
        
        query = db.query(Message).filter(
            Message.conversation_id == conversation_id,
            ~Message.is_deleted
        )
        
        # 总数
        total = query.count()
        
        # 分页，按时间倒序
        offset = (page - 1) * page_size
        messages = query.order_by(desc(Message.created_at)).offset(offset).limit(page_size).all()
        
        # 格式化响应
        items = []
        for msg in messages:
            formatted_msg = await self._format_message_response(db, msg)
            items.append(formatted_msg)
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }

    async def mark_messages_read(
        self,
        db: Session,
        conversation_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """标记对话中的消息为已读"""
        # 验证权限
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            or_(Conversation.user1_id == user_id, Conversation.user2_id == user_id)
        ).first()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="对话不存在或无权限访问")
        
        # 标记消息为已读
        unread_messages = db.query(Message).filter(
            Message.conversation_id == conversation_id,
            Message.receiver_id == user_id,
            ~Message.is_read
        ).all()
        
        for message in unread_messages:
            message.is_read = True
        
        # 重置未读计数
        if conversation.user1_id == user_id:
            conversation.user1_unread_count = 0
        else:
            conversation.user2_unread_count = 0
        
        db.commit()
        
        return {"message": "消息已标记为已读", "count": len(unread_messages)}

    # 系统通知相关方法
    async def create_system_notification(
        self,
        db: Session,
        notification_data: SystemNotificationCreate
    ) -> SystemNotificationResponse:
        """创建系统通知"""
        notification = SystemNotification(**notification_data.dict())
        db.add(notification)
        db.commit()
        db.refresh(notification)
        
        # 如果是发给所有用户的通知，创建用户通知记录
        if notification.target_type == "all":
            users = db.query(User).filter(User.status == 1).all()
            for user in users:
                user_notification = UserNotification(
                    user_id=user.id,
                    notification_id=notification.id
                )
                db.add(user_notification)
        elif notification.target_type == "user" and notification.target_ids:
            for user_id in notification.target_ids:
                user_notification = UserNotification(
                    user_id=user_id,
                    notification_id=notification.id
                )
                db.add(user_notification)
        
        db.commit()
        
        return await self._format_notification_response(notification)

    async def get_user_notifications(
        self,
        db: Session,
        user_id: int,
        notification_type: Optional[str] = None,
        is_read: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """获取用户通知列表"""
        query = db.query(UserNotification).filter(
            UserNotification.user_id == user_id,
            ~UserNotification.is_deleted
        ).join(SystemNotification)
        
        if notification_type:
            query = query.filter(SystemNotification.notification_type == notification_type)
        
        if is_read is not None:
            query = query.filter(UserNotification.is_read == is_read)
        
        # 只显示激活的通知
        query = query.filter(SystemNotification.is_active == True)
        
        # 检查过期时间
        now = datetime.now()
        query = query.filter(
            or_(
                SystemNotification.expire_time.is_(None),
                SystemNotification.expire_time > now
            )
        )
        
        # 总数
        total = query.count()
        
        # 分页
        offset = (page - 1) * page_size
        user_notifications = query.order_by(
            desc(SystemNotification.priority),
            desc(UserNotification.created_at)
        ).offset(offset).limit(page_size).all()
        
        # 格式化响应
        items = []
        for user_notif in user_notifications:
            notification_data = await self._format_notification_response(user_notif.notification)
            notification_data.is_read = user_notif.is_read
            notification_data.read_time = user_notif.read_time
            items.append(notification_data)
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }

    async def mark_notification_read(
        self,
        db: Session,
        user_id: int,
        notification_id: int
    ) -> Dict[str, Any]:
        """标记通知为已读"""
        user_notification = db.query(UserNotification).filter(
            UserNotification.user_id == user_id,
            UserNotification.notification_id == notification_id
        ).first()
        
        if not user_notification:
            raise HTTPException(status_code=404, detail="通知不存在")
        
        user_notification.is_read = True
        user_notification.read_time = func.now()
        db.commit()
        
        return {"message": "通知已标记为已读"}

    async def get_message_stats(
        self,
        db: Session,
        user_id: int
    ) -> MessageStats:
        """获取消息统计"""
        # 对话统计
        total_conversations = db.query(Conversation).filter(
            or_(
                and_(Conversation.user1_id == user_id, ~Conversation.user1_deleted),
                and_(Conversation.user2_id == user_id, ~Conversation.user2_deleted)
            )
        ).count()
        
        # 未读对话数
        unread_conversations = db.query(Conversation).filter(
            or_(
                and_(Conversation.user1_id == user_id, Conversation.user1_unread_count > 0, ~Conversation.user1_deleted),
                and_(Conversation.user2_id == user_id, Conversation.user2_unread_count > 0, ~Conversation.user2_deleted)
            )
        ).count()
        
        # 总未读消息数
        total_unread_messages = db.query(func.sum(
            case(
                (Conversation.user1_id == user_id, Conversation.user1_unread_count),
                else_=Conversation.user2_unread_count
            )
        )).filter(
            or_(Conversation.user1_id == user_id, Conversation.user2_id == user_id)
        ).scalar() or 0
        
        # 系统通知统计
        system_notifications = db.query(UserNotification).filter(
            UserNotification.user_id == user_id,
            ~UserNotification.is_deleted
        ).count()
        
        unread_notifications = db.query(UserNotification).filter(
            UserNotification.user_id == user_id,
            ~UserNotification.is_read,
            ~UserNotification.is_deleted
        ).count()
        
        return MessageStats(
            total_conversations=total_conversations,
            unread_conversations=unread_conversations,
            total_unread_messages=int(total_unread_messages),
            system_notifications=system_notifications,
            unread_notifications=unread_notifications
        )

    # 私有方法：格式化响应
    async def _format_conversation_response(
        self,
        db: Session,
        conversation: Conversation,
        current_user_id: int
    ) -> ConversationResponse:
        """格式化对话响应"""
        # 确定对方用户
        other_user_id = conversation.user2_id if conversation.user1_id == current_user_id else conversation.user1_id
        other_user = db.query(User).filter(User.id == other_user_id).first()
        
        other_user_info = None
        if other_user:
            other_user_info = {
                "id": other_user.id,
                "nickname": other_user.nickname or other_user.username,
                "avatar": other_user.avatar_url,
                "phone": other_user.phone
            }
        
        # 获取最后一条消息内容
        last_message_content = None
        if conversation.last_message_id:
            last_message = db.query(Message).filter(Message.id == conversation.last_message_id).first()
            if last_message:
                last_message_content = last_message.content
        
        # 当前用户的未读数
        unread_count = conversation.user1_unread_count if conversation.user1_id == current_user_id else conversation.user2_unread_count
        
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
            other_user_info=other_user_info,
            last_message_content=last_message_content,
            unread_count=unread_count
        )

    async def _format_message_response(
        self,
        db: Session,
        message: Message
    ) -> MessageResponse:
        """格式化消息响应"""
        # 获取发送者信息
        sender = db.query(User).filter(User.id == message.sender_id).first()
        sender_info = None
        if sender:
            sender_info = {
                "id": sender.id,
                "nickname": sender.nickname or sender.username,
                "avatar": sender.avatar_url
            }
        
        # 获取接收者信息
        receiver = db.query(User).filter(User.id == message.receiver_id).first()
        receiver_info = None
        if receiver:
            receiver_info = {
                "id": receiver.id,
                "nickname": receiver.nickname or receiver.username,
                "avatar": receiver.avatar_url
            }
        
        return MessageResponse(
            id=message.id,
            conversation_id=message.conversation_id,
            sender_id=message.sender_id,
            receiver_id=message.receiver_id,
            message_type=message.message_type,
            content=message.content,
            related_id=message.related_id,
            is_read=message.is_read,
            is_deleted=message.is_deleted,
            created_at=message.created_at,
            sender_info=sender_info,
            receiver_info=receiver_info
        )

    async def _format_notification_response(
        self,
        notification: SystemNotification
    ) -> SystemNotificationResponse:
        """格式化系统通知响应"""
        return SystemNotificationResponse(
            id=notification.id,
            title=notification.title,
            content=notification.content,
            notification_type=notification.notification_type,
            target_type=notification.target_type,
            target_ids=notification.target_ids,
            related_type=notification.related_type,
            related_id=notification.related_id,
            extra_data=notification.extra_data,
            is_active=notification.is_active,
            priority=notification.priority,
            publish_time=notification.publish_time,
            expire_time=notification.expire_time,
            created_at=notification.created_at,
            updated_at=notification.updated_at
        )


# 修复导入问题
from sqlalchemy import case
