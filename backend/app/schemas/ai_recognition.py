from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

class RecognitionRequest(BaseModel):
    """识别请求"""
    image_data: Optional[str] = Field(None, description="Base64编码的图片数据")
    image_format: Optional[str] = Field(None, description="图片格式 (jpg, png, webp等)")
    image_url: Optional[str] = Field(None, description="图片URL地址")
    
    class Config:
        schema_extra = {
            "example": {
                "image_data": "base64编码的图片数据",
                "image_format": "jpg",
                "image_url": "https://example.com/pet.jpg"
            }
        }

class PetEstimatedValue(BaseModel):
    """宠物估价"""
    min_price: int = Field(..., description="最低价格")
    max_price: int = Field(..., description="最高价格") 
    currency: str = Field(default="CNY", description="货币单位")
    factors: List[str] = Field(default=[], description="影响价格的因素")
    note: str = Field(default="", description="价格说明")

class AlternativeBreed(BaseModel):
    """相似品种"""
    breed: str = Field(..., description="品种名称")
    similarity: float = Field(..., description="相似度")
    characteristics: List[str] = Field(default=[], description="特征")

class RecognitionResult(BaseModel):
    """识别结果"""
    pet_type: str = Field(..., description="宠物类型")
    breed: str = Field(..., description="品种名称")
    confidence: float = Field(..., description="置信度")
    characteristics: List[str] = Field(default=[], description="特征描述")
    care_advice: List[str] = Field(default=[], description="护理建议")
    health_tips: List[str] = Field(default=[], description="健康提示")
    feeding_guide: List[str] = Field(default=[], description="喂养指南")
    estimated_value: Optional[PetEstimatedValue] = Field(None, description="估价信息")
    popularity_score: Optional[float] = Field(None, description="流行度评分")
    alternative_breeds: List[AlternativeBreed] = Field(default=[], description="相似品种")

class RecognitionResponse(BaseModel):
    """识别响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[RecognitionResult] = Field(None, description="识别结果")

class RecognitionHistoryItem(BaseModel):
    """识别历史项"""
    id: int = Field(..., description="记录ID")
    pet_type: str = Field(..., description="宠物类型")
    breed: str = Field(..., description="品种名称")
    confidence: float = Field(..., description="置信度")
    created_at: str = Field(..., description="识别时间")
    result_summary: Dict[str, Any] = Field(default={}, description="结果摘要")

class RecognitionHistoryResponse(BaseModel):
    """识别历史响应"""
    items: List[RecognitionHistoryItem] = Field(..., description="历史记录列表")
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页大小")
    total_pages: int = Field(..., description="总页数")

class BreedInfo(BaseModel):
    """品种信息"""
    key: str = Field(..., description="品种标识")
    name: str = Field(..., description="品种名称")
    characteristics: List[str] = Field(default=[], description="特征")
    care_tips: List[str] = Field(default=[], description="护理提示")
    popularity: float = Field(default=0.0, description="流行度")
    price_range: Dict[str, int] = Field(default={}, description="价格范围")

class PetTypeOverview(BaseModel):
    """宠物类型概览"""
    breeds_count: int = Field(..., description="品种数量")
    popular_breeds: List[Dict[str, Any]] = Field(default=[], description="热门品种")

class BreedEncyclopediaResponse(BaseModel):
    """品种百科响应"""
    pet_type: Optional[str] = Field(None, description="宠物类型")
    breeds: List[BreedInfo] = Field(default=[], description="品种列表")
    total_breeds: Optional[int] = Field(None, description="品种总数")
    overview: Optional[Dict[str, PetTypeOverview]] = Field(None, description="类型概览")
    total_types: Optional[int] = Field(None, description="类型总数")

class RecognitionStats(BaseModel):
    """识别统计"""
    recognitions: int = Field(..., description="识别总数")
    unique_users: int = Field(..., description="独立用户数")
    avg_confidence: float = Field(..., description="平均置信度")

class PetTypeStats(BaseModel):
    """宠物类型统计"""
    pet_type: str = Field(..., description="宠物类型")
    count: int = Field(..., description="识别次数")
    avg_confidence: float = Field(..., description="平均置信度")

class PopularBreed(BaseModel):
    """热门品种"""
    breed: str = Field(..., description="品种名称")
    count: int = Field(..., description="识别次数")

class RecentStats(BaseModel):
    """最近统计"""
    count: int = Field(..., description="识别次数")
    avg_confidence: float = Field(..., description="平均置信度")

class RecognitionStatsResponse(BaseModel):
    """识别统计响应"""
    total: RecognitionStats = Field(..., description="总体统计")
    by_pet_type: List[PetTypeStats] = Field(..., description="按宠物类型统计")
    popular_breeds: List[PopularBreed] = Field(..., description="热门品种")
    recent_7_days: RecentStats = Field(..., description="最近7天统计")

class FeedbackRequest(BaseModel):
    """反馈请求"""
    recognition_id: int = Field(..., description="识别记录ID")
    feedback_type: str = Field(..., description="反馈类型: correct, incorrect, partial")
    correct_breed: Optional[str] = Field(None, description="正确品种")
    comments: Optional[str] = Field(None, description="评论")
    rating: Optional[int] = Field(None, ge=1, le=5, description="评分(1-5)")

class ImageQualityCheck(BaseModel):
    """图片质量检查"""
    is_good_quality: bool = Field(..., description="是否高质量")
    score: float = Field(..., description="质量评分")
    issues: List[str] = Field(default=[], description="问题列表")
    suggestions: List[str] = Field(default=[], description="建议列表")

class BatchRecognitionRequest(BaseModel):
    """批量识别请求"""
    images: List[RecognitionRequest] = Field(..., description="图片列表")
    max_concurrent: int = Field(default=3, ge=1, le=10, description="最大并发数")

class BatchRecognitionResponse(BaseModel):
    """批量识别响应"""
    success: bool = Field(..., description="是否成功")
    total_count: int = Field(..., description="总图片数")
    success_count: int = Field(..., description="成功识别数")
    failed_count: int = Field(..., description="失败数")
    results: List[RecognitionResponse] = Field(..., description="识别结果列表")
    errors: List[str] = Field(default=[], description="错误信息")

class RecognitionConfigResponse(BaseModel):
    """识别配置响应"""
    success: bool = Field(..., description="是否成功")
    data: Dict[str, Any] = Field(..., description="配置数据")

class BreedUpdateRequest(BaseModel):
    """品种信息更新请求"""
    pet_type: str = Field(..., description="宠物类型")
    breed_key: str = Field(..., description="品种标识") 
    breed_name: str = Field(..., description="品种名称")
    breed_name_en: Optional[str] = Field(None, description="英文名称")
    characteristics: List[str] = Field(default=[], description="特征")
    care_tips: List[str] = Field(default=[], description="护理建议")
    health_tips: List[str] = Field(default=[], description="健康提示")
    feeding_guide: List[str] = Field(default=[], description="喂养指南")
    price_min: Optional[Decimal] = Field(None, description="最低价格")
    price_max: Optional[Decimal] = Field(None, description="最高价格")
    popularity_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="流行度评分")
    origin_country: Optional[str] = Field(None, description="原产国")
    life_span: Optional[str] = Field(None, description="寿命范围")
    size_category: Optional[str] = Field(None, description="体型分类")

class ModelMetricsResponse(BaseModel):
    """模型性能指标响应"""
    model_version: str = Field(..., description="模型版本")
    accuracy: float = Field(..., description="准确率")
    precision: float = Field(..., description="精确率")
    recall: float = Field(..., description="召回率")
    f1_score: float = Field(..., description="F1分数")
    total_predictions: int = Field(..., description="总预测次数")
    correct_predictions: int = Field(..., description="正确预测次数")
    avg_confidence: float = Field(..., description="平均置信度")
    avg_processing_time: float = Field(..., description="平均处理时间")
    metrics_date: str = Field(..., description="指标日期")

class UserRecognitionStats(BaseModel):
    """用户识别统计"""
    total_recognitions: int = Field(..., description="总识别次数")
    recent_recognitions: int = Field(..., description="最近识别次数")
    avg_confidence: float = Field(..., description="平均置信度")
    most_common_type: Optional[str] = Field(None, description="最常识别类型")
    most_common_count: int = Field(default=0, description="最常识别次数")
    daily_remaining: int = Field(..., description="今日剩余次数")
    daily_limit: int = Field(..., description="每日限制次数")

# 响应基类
class BaseResponse(BaseModel):
    """基础响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[Any] = Field(None, description="数据内容")

class ErrorResponse(BaseModel):
    """错误响应"""
    success: bool = Field(False, description="是否成功")
    message: str = Field(..., description="错误信息")
    error_code: Optional[str] = Field(None, description="错误代码")
    details: Optional[Dict[str, Any]] = Field(None, description="错误详情")