from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.core.database import Base

class SMSCode(Base):
    """短信验证码表"""
    __tablename__ = "sms_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(11), nullable=False, index=True, comment="手机号")
    code = Column(String(6), nullable=False, comment="验证码")
    is_used = Column(Boolean, default=False, comment="是否已使用")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    expires_at = Column(DateTime(timezone=True), nullable=False, comment="过期时间")
    
    def __repr__(self):
        return f"<SMSCode(phone={self.phone}, code={self.code}, is_used={self.is_used})>"
