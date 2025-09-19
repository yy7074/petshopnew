from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, DECIMAL, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class AIRecognitionRecord(Base):
    """AI识别记录模型"""
    __tablename__ = "ai_recognition_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 识别结果
    pet_type = Column(String(50), nullable=False, comment="宠物类型")
    breed = Column(String(100), nullable=False, comment="品种名称") 
    confidence = Column(DECIMAL(5, 4), nullable=False, comment="置信度")
    
    # 详细结果数据
    result_data = Column(JSON, comment="完整识别结果数据")
    
    # 图片信息
    image_format = Column(String(10), comment="图片格式")
    image_size = Column(Integer, comment="图片大小(字节)")
    
    # 识别状态
    status = Column(String(20), default="pending", comment="状态: pending(处理中), completed(完成), failed(失败)")
    error_message = Column(Text, comment="错误信息")
    
    # 处理时间
    processing_time = Column(DECIMAL(8, 3), comment="处理耗时(秒)")
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关联关系
    user = relationship("User", back_populates="ai_recognitions")

class AIRecognitionFeedback(Base):
    """AI识别反馈模型"""
    __tablename__ = "ai_recognition_feedback"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    recognition_id = Column(Integer, ForeignKey("ai_recognition_records.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 反馈内容
    feedback_type = Column(String(20), nullable=False, comment="反馈类型: correct(正确), incorrect(错误), partial(部分正确)")
    correct_breed = Column(String(100), comment="用户认为的正确品种")
    comments = Column(Text, comment="用户评论")
    rating = Column(Integer, comment="评分(1-5)")
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    
    # 关联关系
    recognition = relationship("AIRecognitionRecord")
    user = relationship("User")

class PetBreedInfo(Base):
    """宠物品种信息模型"""
    __tablename__ = "pet_breed_info"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 基本信息
    pet_type = Column(String(50), nullable=False, index=True, comment="宠物类型")
    breed_key = Column(String(100), nullable=False, index=True, comment="品种标识")
    breed_name = Column(String(100), nullable=False, comment="品种名称")
    breed_name_en = Column(String(100), comment="英文名称")
    
    # 特征信息
    characteristics = Column(JSON, comment="特征列表")
    physical_traits = Column(JSON, comment="外观特征")
    temperament = Column(JSON, comment="性格特点")
    
    # 护理信息
    care_tips = Column(JSON, comment="护理建议")
    health_tips = Column(JSON, comment="健康提示")
    feeding_guide = Column(JSON, comment="喂养指南")
    exercise_needs = Column(String(20), comment="运动需求: low(低), medium(中), high(高)")
    
    # 价格信息
    price_min = Column(DECIMAL(10, 2), comment="最低价格")
    price_max = Column(DECIMAL(10, 2), comment="最高价格")
    price_currency = Column(String(10), default="CNY", comment="货币单位")
    
    # 流行度和统计
    popularity_score = Column(DECIMAL(3, 2), default=0.5, comment="流行度评分(0-1)")
    recognition_count = Column(Integer, default=0, comment="被识别次数")
    
    # 其他信息
    origin_country = Column(String(50), comment="原产国")
    life_span = Column(String(20), comment="寿命范围")
    size_category = Column(String(20), comment="体型分类: small(小型), medium(中型), large(大型)")
    
    # 状态
    is_active = Column(Boolean, default=True, comment="是否启用")
    is_verified = Column(Boolean, default=False, comment="是否已验证")
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class AIModelMetrics(Base):
    """AI模型性能指标"""
    __tablename__ = "ai_model_metrics"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 模型信息
    model_version = Column(String(20), nullable=False, comment="模型版本")
    model_type = Column(String(50), nullable=False, comment="模型类型")
    
    # 性能指标
    accuracy = Column(DECIMAL(5, 4), comment="准确率")
    precision = Column(DECIMAL(5, 4), comment="精确率")
    recall = Column(DECIMAL(5, 4), comment="召回率")
    f1_score = Column(DECIMAL(5, 4), comment="F1分数")
    
    # 处理统计
    total_predictions = Column(Integer, default=0, comment="总预测次数")
    correct_predictions = Column(Integer, default=0, comment="正确预测次数")
    avg_confidence = Column(DECIMAL(5, 4), comment="平均置信度")
    avg_processing_time = Column(DECIMAL(8, 3), comment="平均处理时间(秒)")
    
    # 时间范围
    metrics_date = Column(DateTime, nullable=False, comment="指标日期")
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class RecognitionCache(Base):
    """识别结果缓存"""
    __tablename__ = "recognition_cache"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 缓存键值
    image_hash = Column(String(64), nullable=False, unique=True, index=True, comment="图片哈希值")
    
    # 缓存结果
    pet_type = Column(String(50), nullable=False)
    breed = Column(String(100), nullable=False)
    confidence = Column(DECIMAL(5, 4), nullable=False)
    result_data = Column(JSON, comment="完整结果数据")
    
    # 缓存统计
    hit_count = Column(Integer, default=0, comment="命中次数")
    last_accessed = Column(DateTime, server_default=func.now(), comment="最后访问时间")
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, nullable=False, comment="过期时间")