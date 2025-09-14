from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base


class Conversation(Base):
    """对话表"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user1_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user2_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    last_message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    last_message_time = Column(DateTime, nullable=True)
    user1_unread_count = Column(Integer, default=0)
    user2_unread_count = Column(Integer, default=0)
    user1_deleted = Column(Boolean, default=False)
    user2_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关系
    user1 = relationship("User", foreign_keys=[user1_id])
    user2 = relationship("User", foreign_keys=[user2_id])
    last_message = relationship("Message", foreign_keys=[last_message_id], post_update=True)
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", 
                          foreign_keys="Message.conversation_id")
    
    # 索引
    __table_args__ = (
        Index('idx_conversation_users', 'user1_id', 'user2_id'),
        Index('idx_conversation_last_message_time', 'last_message_time'),
    )


class Message(Base):
    """消息表"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message_type = Column(String(20), default="text")  # text, image, product, system
    content = Column(Text, nullable=False)
    related_id = Column(Integer, nullable=True)  # 关联的商品ID等
    is_read = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关系
    conversation = relationship("Conversation", back_populates="messages", foreign_keys=[conversation_id])
    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])
    
    # 索引
    __table_args__ = (
        Index('idx_message_conversation', 'conversation_id'),
        Index('idx_message_sender', 'sender_id'),
        Index('idx_message_receiver', 'receiver_id'),
        Index('idx_message_created_at', 'created_at'),
        Index('idx_message_unread', 'receiver_id', 'is_read'),
    )
