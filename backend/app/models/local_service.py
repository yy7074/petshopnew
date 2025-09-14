from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, DECIMAL, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class LocalServicePost(Base):
    """同城服务基础模型"""
    __tablename__ = "local_service_posts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="发布用户ID")
    service_type = Column(String(50), nullable=False, comment="服务类型: pet_social, local_store, aquarium_design, door_service")
    title = Column(String(200), nullable=False, comment="服务标题")
    description = Column(Text, comment="服务描述")
    content = Column(Text, comment="详细内容")
    
    # 位置信息
    province = Column(String(50), comment="省份")
    city = Column(String(50), comment="城市")
    district = Column(String(50), comment="区县")
    address = Column(String(500), comment="详细地址")
    latitude = Column(DECIMAL(10, 7), comment="纬度")
    longitude = Column(DECIMAL(10, 7), comment="经度")
    
    # 价格信息
    price = Column(DECIMAL(10, 2), comment="服务价格")
    price_unit = Column(String(20), default="元", comment="价格单位")
    
    # 联系信息
    contact_name = Column(String(100), comment="联系人")
    contact_phone = Column(String(20), comment="联系电话")
    contact_wechat = Column(String(100), comment="微信号")
    
    # 额外信息
    extra_data = Column(JSON, comment="额外数据，根据服务类型存储不同字段")
    images = Column(JSON, comment="图片URLs列表")
    tags = Column(JSON, comment="标签列表")
    
    # 状态
    status = Column(Integer, default=1, comment="状态: 1:正常, 2:下架, 3:删除")
    is_featured = Column(Boolean, default=False, comment="是否推荐")
    view_count = Column(Integer, default=0, comment="浏览次数")
    like_count = Column(Integer, default=0, comment="点赞数")
    comment_count = Column(Integer, default=0, comment="评论数")
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    user = relationship("User", back_populates="local_service_posts")
    comments = relationship("LocalServiceComment", back_populates="service", cascade="all, delete-orphan")


class LocalServiceComment(Base):
    """同城服务评论模型"""
    __tablename__ = "local_service_comments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    service_id = Column(Integer, ForeignKey("local_service_posts.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("local_service_comments.id"), comment="父评论ID，用于回复")
    
    content = Column(Text, nullable=False, comment="评论内容")
    images = Column(JSON, comment="评论图片")
    
    status = Column(Integer, default=1, comment="状态: 1:正常, 2:隐藏, 3:删除")
    like_count = Column(Integer, default=0, comment="点赞数")
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    service = relationship("LocalServicePost", back_populates="comments")
    user = relationship("User")
    parent = relationship("LocalServiceComment", remote_side=[id])
    replies = relationship("LocalServiceComment", back_populates="parent")


class LocalServiceLike(Base):
    """同城服务点赞模型"""
    __tablename__ = "local_service_likes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    service_id = Column(Integer, ForeignKey("local_service_posts.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    created_at = Column(DateTime, server_default=func.now())

    # 唯一约束
    __table_args__ = (
        {"mysql_charset": "utf8mb4"},
    )


class LocalServiceFavorite(Base):
    """同城服务收藏模型"""
    __tablename__ = "local_service_favorites"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    service_id = Column(Integer, ForeignKey("local_service_posts.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    created_at = Column(DateTime, server_default=func.now())

    # 唯一约束
    __table_args__ = (
        {"mysql_charset": "utf8mb4"},
    )


class PetSocialPost(Base):
    """宠物交流帖子模型"""
    __tablename__ = "pet_social_posts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False, comment="帖子标题")
    content = Column(Text, nullable=False, comment="帖子内容")
    images = Column(JSON, comment="图片URLs列表")
    
    # 宠物相关信息
    pet_type = Column(String(50), comment="宠物类型")
    pet_breed = Column(String(100), comment="宠物品种")
    pet_age = Column(String(50), comment="宠物年龄")
    pet_gender = Column(String(10), comment="宠物性别")
    
    # 位置信息
    city = Column(String(50), comment="城市")
    district = Column(String(50), comment="区县")
    
    # 分类
    category = Column(String(50), comment="分类: experience, question, show, breeding, lost_found")
    tags = Column(JSON, comment="标签列表")
    
    # 统计
    view_count = Column(Integer, default=0, comment="浏览次数")
    like_count = Column(Integer, default=0, comment="点赞数")
    comment_count = Column(Integer, default=0, comment="评论数")
    share_count = Column(Integer, default=0, comment="分享数")
    
    # 状态
    status = Column(Integer, default=1, comment="状态: 1:正常, 2:隐藏, 3:删除")
    is_top = Column(Boolean, default=False, comment="是否置顶")
    is_featured = Column(Boolean, default=False, comment="是否推荐")
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    user = relationship("User")
    comments = relationship("PetSocialComment", back_populates="post", cascade="all, delete-orphan")


class PetSocialComment(Base):
    """宠物交流评论模型"""
    __tablename__ = "pet_social_comments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey("pet_social_posts.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("pet_social_comments.id"), comment="父评论ID")
    
    content = Column(Text, nullable=False, comment="评论内容")
    images = Column(JSON, comment="评论图片")
    
    status = Column(Integer, default=1, comment="状态: 1:正常, 2:隐藏, 3:删除")
    like_count = Column(Integer, default=0, comment="点赞数")
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    post = relationship("PetSocialPost", back_populates="comments")
    user = relationship("User")
    parent = relationship("PetSocialComment", remote_side=[id])
    replies = relationship("PetSocialComment", back_populates="parent")
