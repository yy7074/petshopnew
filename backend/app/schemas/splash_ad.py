"""
启动广告数据模式定义
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from app.models.splash_ad import AdType, AdStatus

class SplashAdBase(BaseModel):
    """启动广告基础模式"""
    title: str = Field(..., min_length=1, max_length=200, description="广告标题")
    description: Optional[str] = Field(None, description="广告描述")
    ad_type: AdType = Field(default=AdType.IMAGE, description="广告类型")
    image_url: Optional[str] = Field(None, max_length=500, description="图片URL")
    video_url: Optional[str] = Field(None, max_length=500, description="视频URL")
    click_action: Optional[str] = Field(None, max_length=50, description="点击行为")
    target_url: Optional[str] = Field(None, max_length=500, description="目标URL")
    target_id: Optional[int] = Field(None, description="目标ID")
    display_duration: int = Field(default=3, ge=1, le=30, description="显示时长（秒）")
    skip_enabled: bool = Field(default=True, description="是否允许跳过")
    skip_delay: int = Field(default=0, ge=0, le=10, description="跳过按钮延迟显示时间（秒）")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    priority: int = Field(default=0, description="优先级")
    weight: int = Field(default=1, ge=1, description="权重")

    @validator('end_time')
    def validate_end_time(cls, v, values):
        if v and 'start_time' in values and values['start_time']:
            if v <= values['start_time']:
                raise ValueError('结束时间必须晚于开始时间')
        return v

    @validator('image_url', 'video_url')
    def validate_urls(cls, v):
        if v and not (v.startswith('http://') or v.startswith('https://') or v.startswith('/')):
            raise ValueError('URL格式不正确')
        return v

class SplashAdCreate(SplashAdBase):
    """创建启动广告"""
    pass

class SplashAdUpdate(BaseModel):
    """更新启动广告"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="广告标题")
    description: Optional[str] = Field(None, description="广告描述")
    ad_type: Optional[AdType] = Field(None, description="广告类型")
    image_url: Optional[str] = Field(None, max_length=500, description="图片URL")
    video_url: Optional[str] = Field(None, max_length=500, description="视频URL")
    click_action: Optional[str] = Field(None, max_length=50, description="点击行为")
    target_url: Optional[str] = Field(None, max_length=500, description="目标URL")
    target_id: Optional[int] = Field(None, description="目标ID")
    display_duration: Optional[int] = Field(None, ge=1, le=30, description="显示时长（秒）")
    skip_enabled: Optional[bool] = Field(None, description="是否允许跳过")
    skip_delay: Optional[int] = Field(None, ge=0, le=10, description="跳过按钮延迟显示时间（秒）")
    status: Optional[AdStatus] = Field(None, description="广告状态")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    priority: Optional[int] = Field(None, description="优先级")
    weight: Optional[int] = Field(None, ge=1, description="权重")

class SplashAdResponse(SplashAdBase):
    """启动广告响应"""
    id: int
    status: AdStatus
    view_count: int = 0
    click_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SplashAdListResponse(BaseModel):
    """启动广告列表响应"""
    items: List[SplashAdResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

class SplashAdStatsUpdate(BaseModel):
    """广告统计更新"""
    action: str = Field(..., description="操作类型: view, click")

class SplashAdClientResponse(BaseModel):
    """客户端广告响应（简化版）"""
    id: int
    ad_type: str
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    click_action: Optional[str] = None
    target_url: Optional[str] = None
    target_id: Optional[int] = None
    display_duration: int
    skip_enabled: bool
    skip_delay: int

    class Config:
        from_attributes = True
