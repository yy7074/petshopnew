from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, DECIMAL, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    phone = Column(String(20), unique=True, index=True, nullable=False)
    email = Column(String(100), index=True)
    password_hash = Column(String(255), nullable=False)
    avatar_url = Column(String(500))
    nickname = Column(String(50))
    real_name = Column(String(50))
    gender = Column(Integer, default=0, comment="0:未知,1:男,2:女")
    birth_date = Column(Date)
    location = Column(String(100))
    is_seller = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    balance = Column(DECIMAL(10, 2), default=0.00)
    credit_score = Column(Integer, default=100)
    status = Column(Integer, default=1, comment="1:正常,2:冻结,3:禁用")
    last_login_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关联关系
    # wallet_transactions = relationship("WalletTransaction", back_populates="user")
    # deposits = relationship("Deposit", back_populates="user")
    # lottery_records = relationship("LotteryRecord", back_populates="user")
    # 暂时注释掉所有关系，避免错误

class UserFollow(Base):
    __tablename__ = "user_follows"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    follower_id = Column(Integer, nullable=False, index=True)
    following_id = Column(Integer, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())

class UserAddress(Base):
    __tablename__ = "user_addresses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    receiver_name = Column(String(50), nullable=False)
    phone = Column(String(20), nullable=False)
    province = Column(String(50), nullable=False)
    city = Column(String(50), nullable=False)
    district = Column(String(50), nullable=False)
    detail_address = Column(String(200), nullable=False)
    postal_code = Column(String(10))
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class UserCheckin(Base):
    __tablename__ = "user_checkins"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    checkin_date = Column(Date, nullable=False)
    consecutive_days = Column(Integer, default=1)
    reward_points = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())

class KeywordSubscription(Base):
    __tablename__ = "keyword_subscriptions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    keyword = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


