from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, DECIMAL, JSON
from sqlalchemy.sql import func
from app.core.database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    parent_id = Column(Integer, default=0)
    icon_url = Column(String(500))
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    seller_id = Column(Integer, nullable=False, index=True)
    category_id = Column(Integer, nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    images = Column(JSON, comment="商品图片数组")
    starting_price = Column(DECIMAL(10, 2), nullable=False)
    current_price = Column(DECIMAL(10, 2), nullable=False)
    buy_now_price = Column(DECIMAL(10, 2), comment="一口价")
    auction_type = Column(Integer, default=1, comment="1:拍卖,2:一口价,3:混合")
    auction_start_time = Column(DateTime)
    auction_end_time = Column(DateTime)
    location = Column(String(100))
    shipping_fee = Column(DECIMAL(8, 2), default=0.00)
    is_free_shipping = Column(Boolean, default=False)
    condition_type = Column(Integer, default=1, comment="1:全新,2:二手,3:其他")
    stock_quantity = Column(Integer, default=1)
    view_count = Column(Integer, default=0)
    bid_count = Column(Integer, default=0)
    favorite_count = Column(Integer, default=0)
    status = Column(Integer, default=1, comment="1:待审核,2:拍卖中,3:已结束,4:已下架")
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Bid(Base):
    __tablename__ = "bids"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, nullable=False, index=True)
    bidder_id = Column(Integer, nullable=False, index=True)
    bid_amount = Column(DECIMAL(10, 2), nullable=False)
    is_auto_bid = Column(Boolean, default=False)
    max_bid_amount = Column(DECIMAL(10, 2))
    status = Column(Integer, default=1, comment="1:有效,2:被超越,3:撤销")
    created_at = Column(DateTime, server_default=func.now())

class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, nullable=False, index=True)
    image_url = Column(String(500), nullable=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())

class ProductFavorite(Base):
    __tablename__ = "product_favorites"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    product_id = Column(Integer, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())

class Shop(Base):
    __tablename__ = "shops"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    owner_id = Column(Integer, nullable=False, index=True)
    shop_name = Column(String(100), nullable=False)
    shop_logo = Column(String(500))
    description = Column(Text)
    business_license = Column(String(100))
    contact_phone = Column(String(20))
    address = Column(String(200))
    rating = Column(DECIMAL(3, 2), default=5.00)
    total_sales = Column(Integer, default=0)
    status = Column(Integer, default=1, comment="1:正常,2:暂停,3:关闭")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class LocalService(Base):
    __tablename__ = "local_services"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    provider_id = Column(Integer, nullable=False, index=True)
    service_type = Column(Integer, nullable=False, comment="1:上门服务,2:宠物交流,3:鱼缸造景")
    title = Column(String(200), nullable=False)
    description = Column(Text)
    images = Column(JSON)
    price = Column(DECIMAL(10, 2))
    location = Column(String(100))
    contact_info = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class SpecialEvent(Base):
    __tablename__ = "special_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    banner_image = Column(String(500))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class AutoBid(Base):
    __tablename__ = "auto_bids"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    max_amount = Column(DECIMAL(10, 2), nullable=False)
    increment_amount = Column(DECIMAL(10, 2), default=1.00)
    status = Column(String(20), default="active", comment="active:活跃, paused:暂停, completed:完成, cancelled:取消")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class EventProduct(Base):
    __tablename__ = "event_products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    event_id = Column(Integer, nullable=False, index=True)
    product_id = Column(Integer, nullable=False, index=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())










