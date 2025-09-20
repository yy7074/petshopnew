from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class UserFollow(Base):
    __tablename__ = "user_follows"

    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)  # 关注者
    following_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)  # 被关注者
    created_at = Column(DateTime, server_default=func.now())
    
    # 关联关系
    follower = relationship("User", foreign_keys=[follower_id], back_populates="following")
    following = relationship("User", foreign_keys=[following_id], back_populates="followers")


class BrowseHistory(Base):
    __tablename__ = "browse_histories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    product_title = Column(String(255), nullable=False)  # 冗余存储，防止商品删除后历史记录丢失
    product_image = Column(String(500))
    product_price = Column(String(20))
    seller_name = Column(String(100))
    seller_location = Column(String(100))
    product_type = Column(String(20))  # auction, fixed
    product_status = Column(String(20))  # 拍卖中, 一口价, 已结束等
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关联关系
    user = relationship("User", back_populates="browse_histories")