from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, DECIMAL
from sqlalchemy.sql import func
from app.core.database import Base

class StoreApplication(Base):
    """店铺申请模型"""
    __tablename__ = "store_applications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True, comment="申请用户ID")
    
    # 店铺基本信息
    store_name = Column(String(100), nullable=False, comment="店铺名称")
    store_description = Column(Text, comment="店铺介绍")
    store_type = Column(String(20), nullable=False, comment="店铺类型：个人店、个体商家、企业店、旗舰店")
    
    # 退货地址信息
    consignee_name = Column(String(50), nullable=False, comment="收货人姓名")
    consignee_phone = Column(String(20), nullable=False, comment="收货人电话")
    return_region = Column(String(200), nullable=False, comment="退货地区")
    return_address = Column(String(500), nullable=False, comment="详细地址")
    
    # 实名信息
    real_name = Column(String(50), nullable=False, comment="真实姓名")
    id_number = Column(String(18), nullable=False, comment="身份证号")
    id_start_date = Column(String(10), nullable=False, comment="身份证开始日期")
    id_end_date = Column(String(10), nullable=False, comment="身份证结束日期")
    
    # 证件照片
    id_front_image = Column(String(500), comment="身份证人像面照片")
    id_back_image = Column(String(500), comment="身份证国徽面照片")
    business_license_image = Column(String(500), comment="营业执照照片")
    
    # 申请状态
    status = Column(Integer, default=0, comment="申请状态：0:待审核,1:审核通过,2:审核拒绝,3:已开店")
    reject_reason = Column(Text, comment="拒绝原因")
    
    # 审核信息
    reviewer_id = Column(Integer, comment="审核员ID")
    reviewed_at = Column(DateTime, comment="审核时间")
    
    # 费用信息
    deposit_amount = Column(DECIMAL(10, 2), default=0.00, comment="押金金额")
    annual_fee = Column(DECIMAL(10, 2), default=188.00, comment="年费")
    payment_status = Column(Integer, default=0, comment="支付状态：0:未支付,1:已支付")
    paid_at = Column(DateTime, comment="支付时间")
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
