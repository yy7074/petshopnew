from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .base import Base

class ServiceType(enum.Enum):
    PET_SOCIAL = "pet_social"        # 宠物交流
    PET_BREEDING = "pet_breeding"    # 宠物配种
    LOCAL_STORE = "local_store"      # 本地宠店
    AQUARIUM_DESIGN = "aquarium_design"  # 鱼缸造景
    LOCAL_PICKUP = "local_pickup"    # 同城快取
    DOOR_SERVICE = "door_service"    # 上门服务
    PET_VALUATION = "pet_valuation"  # 宠物估价
    NEARBY = "nearby"                # 附近发现

class ServiceStatus(enum.Enum):
    PENDING = "pending"      # 待审核
    ACTIVE = "active"        # 进行中
    COMPLETED = "completed"  # 已完成
    CANCELLED = "cancelled"  # 已取消

# 宠物交流帖子
class PetSocialPost(Base):
    __tablename__ = "pet_social_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    images = Column(Text)  # JSON格式存储图片URL列表
    pet_type = Column(String(50))  # 宠物类型
    location = Column(String(200))  # 位置
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    is_top = Column(Boolean, default=False)  # 是否置顶
    status = Column(Enum(ServiceStatus), default=ServiceStatus.ACTIVE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联关系
    user = relationship("User", back_populates="social_posts")
    comments = relationship("PetSocialComment", back_populates="post", cascade="all, delete-orphan")

# 宠物交流评论
class PetSocialComment(Base):
    __tablename__ = "pet_social_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("pet_social_posts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    parent_id = Column(Integer, ForeignKey("pet_social_comments.id"))  # 回复评论
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关联关系
    post = relationship("PetSocialPost", back_populates="comments")
    user = relationship("User")
    parent = relationship("PetSocialComment", remote_side=[id])
    replies = relationship("PetSocialComment", remote_side=[parent_id])

# 宠物配种信息
class PetBreedingInfo(Base):
    __tablename__ = "pet_breeding_info"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    pet_name = Column(String(100), nullable=False)
    pet_type = Column(String(50), nullable=False)  # 狗/猫/其他
    breed = Column(String(100), nullable=False)    # 品种
    gender = Column(String(10), nullable=False)    # 性别
    age = Column(Integer, nullable=False)          # 年龄(月)
    weight = Column(Float)                         # 体重(kg)
    health_status = Column(String(200))            # 健康状况
    vaccination_status = Column(String(200))       # 疫苗情况
    images = Column(Text)                          # 宠物照片
    description = Column(Text)                     # 详细描述
    requirements = Column(Text)                    # 配种要求
    location = Column(String(200), nullable=False) # 所在地区
    contact_phone = Column(String(20))             # 联系电话
    contact_wechat = Column(String(50))            # 微信号
    price = Column(Float)                          # 配种费用
    is_available = Column(Boolean, default=True)   # 是否可配种
    status = Column(Enum(ServiceStatus), default=ServiceStatus.ACTIVE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联关系
    user = relationship("User")

# 本地宠店信息
class LocalPetStore(Base):
    __tablename__ = "local_pet_stores"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    owner_name = Column(String(100))
    phone = Column(String(20), nullable=False)
    address = Column(String(500), nullable=False)
    latitude = Column(Float)   # 纬度
    longitude = Column(Float)  # 经度
    business_hours = Column(String(200))  # 营业时间
    services = Column(Text)    # 提供的服务，JSON格式
    images = Column(Text)      # 店铺照片
    description = Column(Text) # 店铺描述
    rating = Column(Float, default=0.0)     # 评分
    review_count = Column(Integer, default=0) # 评价数量
    is_verified = Column(Boolean, default=False)  # 是否认证
    status = Column(Enum(ServiceStatus), default=ServiceStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# 鱼缸造景服务
class AquariumDesignService(Base):
    __tablename__ = "aquarium_design_services"
    
    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    tank_sizes = Column(Text)      # 支持的鱼缸尺寸，JSON格式
    design_styles = Column(Text)   # 设计风格，JSON格式
    price_range = Column(String(100))  # 价格区间
    portfolio_images = Column(Text)    # 作品集图片
    location = Column(String(200), nullable=False)
    contact_phone = Column(String(20))
    contact_wechat = Column(String(50))
    rating = Column(Float, default=0.0)
    order_count = Column(Integer, default=0)
    is_available = Column(Boolean, default=True)
    status = Column(Enum(ServiceStatus), default=ServiceStatus.ACTIVE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联关系
    provider = relationship("User")

# 同城快取服务
class LocalPickupService(Base):
    __tablename__ = "local_pickup_services"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    pickup_location = Column(String(500), nullable=False)  # 自取地点
    available_times = Column(Text)     # 可取时间，JSON格式
    contact_phone = Column(String(20), nullable=False)
    contact_person = Column(String(100), nullable=False)  # 联系人
    notes = Column(Text)               # 备注信息
    status = Column(Enum(ServiceStatus), default=ServiceStatus.ACTIVE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联关系
    user = relationship("User")
    product = relationship("Product")

# 上门服务
class DoorService(Base):
    __tablename__ = "door_services"
    
    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    service_name = Column(String(200), nullable=False)
    service_type = Column(String(100), nullable=False)  # 服务类型：美容、医疗、训练等
    description = Column(Text, nullable=False)
    service_area = Column(String(200), nullable=False)  # 服务区域
    price = Column(Float, nullable=False)
    duration = Column(Integer)         # 服务时长(分钟)
    equipment_needed = Column(Text)    # 需要的设备
    images = Column(Text)              # 服务图片
    contact_phone = Column(String(20), nullable=False)
    rating = Column(Float, default=0.0)
    order_count = Column(Integer, default=0)
    is_available = Column(Boolean, default=True)
    status = Column(Enum(ServiceStatus), default=ServiceStatus.ACTIVE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联关系
    provider = relationship("User")

# 宠物估价服务
class PetValuationService(Base):
    __tablename__ = "pet_valuation_services"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    pet_type = Column(String(50), nullable=False)
    breed = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(10), nullable=False)
    weight = Column(Float)
    health_status = Column(String(200))
    special_features = Column(Text)    # 特殊特征
    images = Column(Text, nullable=False)  # 宠物照片
    estimated_value = Column(Float)    # 估价结果
    valuator_id = Column(Integer, ForeignKey("users.id"))  # 估价师
    valuation_notes = Column(Text)     # 估价说明
    status = Column(Enum(ServiceStatus), default=ServiceStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联关系
    user = relationship("User", foreign_keys=[user_id])
    valuator = relationship("User", foreign_keys=[valuator_id])

# 附近发现
class NearbyItem(Base):
    __tablename__ = "nearby_items"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)  # 分类：宠物、用品、服务等
    price = Column(Float)
    images = Column(Text)
    location = Column(String(200), nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    contact_phone = Column(String(20))
    contact_wechat = Column(String(50))
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    is_top = Column(Boolean, default=False)
    status = Column(Enum(ServiceStatus), default=ServiceStatus.ACTIVE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联关系
    user = relationship("User")

