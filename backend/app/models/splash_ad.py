"""
启动广告模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class AdType(enum.Enum):
    """广告类型"""
    IMAGE = "image"  # 图片广告
    VIDEO = "video"  # 视频广告

class AdStatus(enum.Enum):
    """广告状态"""
    DRAFT = "draft"      # 草稿
    ACTIVE = "active"    # 激活
    INACTIVE = "inactive" # 停用
    EXPIRED = "expired"   # 已过期

class SplashAd(Base):
    """启动广告模型"""
    __tablename__ = "splash_ads"
    
    id = Column(Integer, primary_key=True, index=True, comment="广告ID")
    title = Column(String(200), nullable=False, comment="广告标题")
    description = Column(Text, comment="广告描述")
    
    # 广告内容
    ad_type = Column(Enum(AdType), nullable=False, default=AdType.IMAGE, comment="广告类型")
    image_url = Column(String(500), comment="图片URL")
    video_url = Column(String(500), comment="视频URL")
    
    # 跳转设置
    click_action = Column(String(50), comment="点击行为: none, url, product, category")
    target_url = Column(String(500), comment="目标URL")
    target_id = Column(Integer, comment="目标ID（商品ID、分类ID等）")
    
    # 显示设置
    display_duration = Column(Integer, default=3, comment="显示时长（秒）")
    skip_enabled = Column(Boolean, default=True, comment="是否允许跳过")
    skip_delay = Column(Integer, default=0, comment="跳过按钮延迟显示时间（秒）")
    
    # 状态和时间
    status = Column(Enum(AdStatus), nullable=False, default=AdStatus.DRAFT, comment="广告状态")
    start_time = Column(DateTime, comment="开始时间")
    end_time = Column(DateTime, comment="结束时间")
    
    # 统计信息
    view_count = Column(Integer, default=0, comment="展示次数")
    click_count = Column(Integer, default=0, comment="点击次数")
    
    # 优先级和权重
    priority = Column(Integer, default=0, comment="优先级（数值越大优先级越高）")
    weight = Column(Integer, default=1, comment="权重（用于随机展示）")
    
    # 创建和更新时间
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'ad_type': self.ad_type.value if self.ad_type else None,
            'image_url': self.image_url,
            'video_url': self.video_url,
            'click_action': self.click_action,
            'target_url': self.target_url,
            'target_id': self.target_id,
            'display_duration': self.display_duration,
            'skip_enabled': self.skip_enabled,
            'skip_delay': self.skip_delay,
            'status': self.status.value if self.status else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'view_count': self.view_count,
            'click_count': self.click_count,
            'priority': self.priority,
            'weight': self.weight,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
