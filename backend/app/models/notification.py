from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class SystemNotification(Base):
    """系统通知表"""
    __tablename__ = "system_notifications"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False, comment="通知标题")
    content = Column(Text, nullable=False, comment="通知内容")
    notification_type = Column(String(50), nullable=False, comment="通知类型: system, auction, order, payment")
    target_type = Column(String(20), default="all", comment="目标类型: all, user, group")
    target_ids = Column(JSON, comment="目标用户ID列表，target_type为user时使用")
    
    # 关联信息
    related_type = Column(String(50), comment="关联类型: product, order, auction")
    related_id = Column(Integer, comment="关联ID")
    extra_data = Column(JSON, comment="额外数据")
    
    # 显示控制
    is_active = Column(Boolean, default=True, comment="是否激活")
    priority = Column(Integer, default=0, comment="优先级，数字越大优先级越高")
    
    # 时间控制
    publish_time = Column(DateTime, comment="发布时间，为空则立即发布")
    expire_time = Column(DateTime, comment="过期时间")
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class UserNotification(Base):
    """用户通知状态表"""
    __tablename__ = "user_notifications"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    notification_id = Column(Integer, ForeignKey("system_notifications.id"), nullable=False)
    
    is_read = Column(Boolean, default=False, comment="是否已读")
    is_deleted = Column(Boolean, default=False, comment="是否删除")
    read_time = Column(DateTime, comment="阅读时间")
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关系
    user = relationship("User")
    notification = relationship("SystemNotification")
    
    # 唯一约束
    __table_args__ = (
        {"mysql_charset": "utf8mb4"},
    )


class MessageTemplate(Base):
    """消息模板表"""
    __tablename__ = "message_templates"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    template_code = Column(String(100), nullable=False, unique=True, comment="模板代码")
    template_name = Column(String(200), nullable=False, comment="模板名称")
    title_template = Column(String(500), comment="标题模板")
    content_template = Column(Text, nullable=False, comment="内容模板")
    notification_type = Column(String(50), nullable=False, comment="通知类型")
    
    # 模板变量说明
    variables = Column(JSON, comment="模板变量说明")
    
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
