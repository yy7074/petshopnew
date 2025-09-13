from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..core.database import Base
from datetime import datetime

class WalletTransaction(Base):
    """钱包交易记录"""
    __tablename__ = "wallet_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    type = Column(String(20), nullable=False)  # recharge, consumption, refund
    amount = Column(DECIMAL(10, 2), nullable=False)
    balance_after = Column(DECIMAL(10, 2), nullable=False)
    description = Column(Text)
    status = Column(String(20), default="pending")  # pending, completed, failed
    order_id = Column(String(50), unique=True, index=True)  # 支付订单ID
    payment_method = Column(String(20))  # alipay, wechat, bank
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # 关联关系
    user = relationship("User", back_populates="wallet_transactions")
