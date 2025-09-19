from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Deposit(Base):
    """保证金模型"""
    __tablename__ = "deposits"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    auction_id = Column(Integer, nullable=True, index=True)  # 关联的拍卖ID，可为空表示通用保证金
    amount = Column(DECIMAL(10, 2), nullable=False)
    type = Column(String(20), nullable=False, comment="缴纳类型: auction(拍卖保证金), general(通用保证金)")
    status = Column(String(20), default="active", comment="状态: active(活跃), frozen(冻结), refunded(已退还), forfeited(没收)")
    description = Column(String(255), comment="描述")
    payment_method = Column(String(20), default="balance", comment="支付方式: balance(余额支付), alipay(支付宝)")
    transaction_id = Column(String(100), comment="交易单号")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    refunded_at = Column(DateTime, comment="退还时间")
    
    # 关联关系
    # user = relationship("User", back_populates="deposits")

class DepositLog(Base):
    """保证金操作日志"""
    __tablename__ = "deposit_logs"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    deposit_id = Column(Integer, ForeignKey("deposits.id"), nullable=False, index=True)
    action = Column(String(20), nullable=False, comment="操作类型: pay(缴纳), freeze(冻结), unfreeze(解冻), refund(退还), forfeit(没收)")
    amount = Column(DECIMAL(10, 2), nullable=False)
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="操作人ID，系统操作时为空")
    reason = Column(String(255), comment="操作原因")
    created_at = Column(DateTime, server_default=func.now())
    
    # 关联关系
    deposit = relationship("Deposit")
    operator = relationship("User")