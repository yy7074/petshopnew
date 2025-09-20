from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from ..core.database import Base

class LotteryPrize(Base):
    """抽奖奖品表"""
    __tablename__ = "lottery_prizes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="奖品名称")
    type = Column(String(20), nullable=False, comment="奖品类型: voucher/coupon/pet")
    value = Column(Float, nullable=True, comment="奖品价值（元）")
    icon = Column(String(200), nullable=True, comment="奖品图标")
    color = Column(String(7), default="#FFD700", comment="转盘显示颜色")
    probability = Column(Float, nullable=False, comment="中奖概率(0-1)")
    stock = Column(Integer, default=-1, comment="库存数量，-1表示无限")
    is_active = Column(Boolean, default=True, comment="是否启用")
    description = Column(Text, nullable=True, comment="奖品描述")
    sort_order = Column(Integer, default=0, comment="排序")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class LotteryRecord(Base):
    """抽奖记录表"""
    __tablename__ = "lottery_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    prize_id = Column(Integer, ForeignKey("lottery_prizes.id"), nullable=True)
    prize_name = Column(String(100), nullable=False, comment="中奖奖品名称")
    prize_type = Column(String(20), nullable=False, comment="奖品类型")
    prize_value = Column(Float, nullable=True, comment="奖品价值")
    is_claimed = Column(Boolean, default=False, comment="是否已领取")
    claimed_at = Column(DateTime, nullable=True, comment="领取时间")
    ip_address = Column(String(45), nullable=True, comment="抽奖IP")
    user_agent = Column(String(500), nullable=True, comment="用户代理")
    created_at = Column(DateTime, default=func.now())
    
    # 关联关系
    # user = relationship("User", back_populates="lottery_records")
    prize = relationship("LotteryPrize")

class LotteryConfig(Base):
    """抽奖配置表"""
    __tablename__ = "lottery_config"
    
    id = Column(Integer, primary_key=True, index=True)
    max_daily_draws = Column(Integer, default=3, comment="每日最大抽奖次数")
    cost_per_draw = Column(Integer, default=0, comment="每次抽奖消耗钻石数")
    is_active = Column(Boolean, default=True, comment="抽奖是否开启")
    start_time = Column(DateTime, nullable=True, comment="活动开始时间")
    end_time = Column(DateTime, nullable=True, comment="活动结束时间")
    description = Column(Text, nullable=True, comment="活动描述")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
