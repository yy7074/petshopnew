from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, DECIMAL, JSON
from sqlalchemy.sql import func
from app.core.database import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_no = Column(String(32), unique=True, nullable=False, index=True)
    buyer_id = Column(Integer, nullable=False, index=True)
    seller_id = Column(Integer, nullable=False, index=True)
    product_id = Column(Integer, nullable=False, index=True)
    final_price = Column(DECIMAL(10, 2), nullable=False)
    shipping_fee = Column(DECIMAL(8, 2), default=0.00)
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    payment_method = Column(Integer, comment="1:支付宝,2:微信,3:银行卡")
    payment_status = Column(Integer, default=1, comment="1:待支付,2:已支付,3:已退款")
    order_status = Column(Integer, default=1, comment="1:待支付,2:待发货,3:已发货,4:已收货,5:已完成,6:已取消")
    shipping_address = Column(JSON, comment="收货地址信息")
    tracking_number = Column(String(50))
    shipped_at = Column(DateTime)
    received_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sender_id = Column(Integer, index=True)
    receiver_id = Column(Integer, nullable=False, index=True)
    message_type = Column(Integer, default=1, comment="1:系统消息,2:私信,3:拍卖通知,4:订单通知")
    title = Column(String(100))
    content = Column(Text, nullable=False)
    related_id = Column(Integer, comment="关联的商品或订单ID")
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())


