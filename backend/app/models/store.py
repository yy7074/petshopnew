from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, DECIMAL, JSON
from sqlalchemy.sql import func
from app.core.database import Base

class Store(Base):
    """店铺模型"""
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    owner_id = Column(Integer, nullable=False, index=True, comment="店主用户ID")
    name = Column(String(100), nullable=False, comment="店铺名称")
    description = Column(Text, comment="店铺描述")
    avatar = Column(String(500), comment="店铺头像")
    banner = Column(String(500), comment="店铺横幅")
    location = Column(String(200), comment="店铺地址")
    phone = Column(String(20), comment="联系电话")
    
    # 店铺设置
    is_open = Column(Boolean, default=True, comment="是否营业中")
    business_hours = Column(JSON, comment="营业时间")
    announcement = Column(Text, comment="店铺公告")
    
    # 统计信息
    total_products = Column(Integer, default=0, comment="商品总数")
    total_sales = Column(Integer, default=0, comment="总销量")
    total_revenue = Column(DECIMAL(12, 2), default=0.00, comment="总收入")
    rating = Column(DECIMAL(3, 2), default=5.00, comment="店铺评分")
    rating_count = Column(Integer, default=0, comment="评分数量")
    follower_count = Column(Integer, default=0, comment="关注数量")
    
    # 状态
    status = Column(Integer, default=1, comment="状态:1:正常,2:暂停,3:关闭")
    verified = Column(Boolean, default=False, comment="是否认证")
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class StoreFollow(Base):
    """店铺关注模型"""
    __tablename__ = "store_follows"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True, comment="用户ID")
    store_id = Column(Integer, nullable=False, index=True, comment="店铺ID")
    created_at = Column(DateTime, server_default=func.now())

class StoreReview(Base):
    """店铺评价模型"""
    __tablename__ = "store_reviews"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True, comment="用户ID")
    store_id = Column(Integer, nullable=False, index=True, comment="店铺ID")
    order_id = Column(Integer, nullable=False, index=True, comment="订单ID")
    rating = Column(Integer, nullable=False, comment="评分1-5")
    comment = Column(Text, comment="评价内容")
    images = Column(JSON, comment="评价图片")
    
    # 店主回复
    reply = Column(Text, comment="店主回复")
    replied_at = Column(DateTime, comment="回复时间")
    
    status = Column(Integer, default=1, comment="状态:1:正常,2:隐藏")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())