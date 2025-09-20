from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Checkin(Base):
    __tablename__ = "checkins"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    checkin_date = Column(String, nullable=False)  # YYYY-MM-DD格式
    consecutive_days = Column(Integer, default=1)  # 连续签到天数
    reward_points = Column(Integer, default=10)  # 奖励钻石数
    is_milestone = Column(Boolean, default=False)  # 是否是里程碑奖励
    milestone_reward = Column(Integer, default=0)  # 里程碑额外奖励
    created_at = Column(DateTime, server_default=func.now())

    # 关联用户
    user = relationship("User", back_populates="checkins")