#!/usr/bin/env python3
"""
演示数据初始化脚本
创建专场和商品数据供前端测试使用
"""

import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.product import (
    Category, Product, SpecialEvent, EventProduct, 
    ProductImage, Shop
)

def create_demo_data():
    """创建演示数据"""
    db = SessionLocal()
    
    try:
        print("🚀 开始创建演示数据...")
        
        # 1. 创建分类
        print("📁 创建商品分类...")
        categories = [
            Category(
                id=1,
                name="宠物",
                parent_id=0,
                icon_url="https://picsum.photos/64/64?random=cat",
                sort_order=1,
                is_active=True
            ),
            Category(
                id=2, 
                name="水族",
                parent_id=0,
                icon_url="https://picsum.photos/64/64?random=fish",
                sort_order=2,
                is_active=True
            ),
            Category(
                id=3,
                name="用品",
                parent_id=0,
                icon_url="https://picsum.photos/64/64?random=toy",
                sort_order=3,
                is_active=True
            ),
        ]
        
        for category in categories:
            existing = db.query(Category).filter(Category.id == category.id).first()
            if not existing:
                db.add(category)
        
        # 2. 创建商店
        print("🏪 创建演示商店...")
        shops = [
            Shop(
                id=1,
                owner_id=2,  # 假设seller_id=2的用户
                shop_name="萌宠天堂",
                shop_logo="https://picsum.photos/100/100?random=shop1",
                description="专业宠物繁育基地，提供优质宠物",
                contact_phone="400-123-4567",
                address="北京市朝阳区",
                rating=Decimal("4.8"),
                total_sales=158,
                status=1
            ),
            Shop(
                id=2,
                owner_id=2,
                shop_name="水族世界", 
                shop_logo="https://picsum.photos/100/100?random=shop2",
                description="专业水族器材和观赏鱼销售",
                contact_phone="400-987-6543",
                address="上海市浦东新区",
                rating=Decimal("4.6"),
                total_sales=89,
                status=1
            ),
        ]
        
        for shop in shops:
            existing = db.query(Shop).filter(Shop.id == shop.id).first()
            if not existing:
                db.add(shop)
        
        # 3. 创建专场活动
        print("🎯 创建专场活动...")
        now = datetime.now()
        events = [
            SpecialEvent(
                id=1,
                title="新春萌宠专场",
                description="新春特惠，精选优质宠物，限时拍卖！",
                banner_image="https://picsum.photos/800/400?random=event1",
                start_time=now - timedelta(days=1),
                end_time=now + timedelta(days=7),
                is_active=True
            ),
            SpecialEvent(
                id=2,
                title="水族精品专场",
                description="精品观赏鱼和水族用品，打造完美水族世界",
                banner_image="https://picsum.photos/800/400?random=event2", 
                start_time=now - timedelta(hours=12),
                end_time=now + timedelta(days=5),
                is_active=True
            ),
            SpecialEvent(
                id=3,
                title="一口价精选",
                description="精选优质商品，一口价直接购买，无需等待",
                banner_image="https://picsum.photos/800/400?random=event3",
                start_time=now - timedelta(days=2),
                end_time=now + timedelta(days=10),
                is_active=True
            ),
        ]
        
        for event in events:
            existing = db.query(SpecialEvent).filter(SpecialEvent.id == event.id).first()
            if not existing:
                db.add(event)
        
        # 4. 创建商品
        print("🐾 创建演示商品...")
        products = [
            # 宠物专场商品
            Product(
                id=1,
                seller_id=2,
                category_id=1,
                title="纯种英短蓝猫 - 品相优秀",
                description="健康活泼的英短蓝猫，疫苗齐全，品相优秀，性格温顺。包健康包纯种，支持上门看猫。",
                images=["https://picsum.photos/400/400?random=cat1", "https://picsum.photos/400/400?random=cat2"],
                starting_price=Decimal("800.00"),
                current_price=Decimal("800.00"),
                buy_now_price=Decimal("1500.00"),
                auction_type=1,
                auction_start_time=now - timedelta(hours=2),
                auction_end_time=now + timedelta(hours=22),
                location="北京市",
                shipping_fee=Decimal("50.00"),
                is_free_shipping=False,
                condition_type=1,
                stock_quantity=1,
                view_count=156,
                bid_count=8,
                favorite_count=23,
                status=2,
                is_featured=True
            ),
            Product(
                id=2,
                seller_id=2,
                category_id=1,
                title="金毛幼犬 - 疫苗齐全",
                description="2个月大金毛幼犬，疫苗已打，驱虫完成。父母都是纯种金毛，小狗活泼健康。",
                images=["https://picsum.photos/400/400?random=dog1", "https://picsum.photos/400/400?random=dog2"],
                starting_price=Decimal("600.00"),
                current_price=Decimal("750.00"),
                buy_now_price=Decimal("1200.00"),
                auction_type=1,
                auction_start_time=now - timedelta(hours=5),
                auction_end_time=now + timedelta(hours=19),
                location="上海市",
                shipping_fee=Decimal("80.00"),
                is_free_shipping=False,
                condition_type=1,
                stock_quantity=1,
                view_count=89,
                bid_count=12,
                favorite_count=31,
                status=2,
                is_featured=True
            ),
            # 水族专场商品
            Product(
                id=3,
                seller_id=2,
                category_id=2,
                title="泰国斗鱼 - 炫彩品种",
                description="精品泰国斗鱼，色彩鲜艳，鱼鳍完整。适合新手饲养，生命力强。",
                images=["https://picsum.photos/400/400?random=fish1", "https://picsum.photos/400/400?random=fish2"],
                starting_price=Decimal("50.00"),
                current_price=Decimal("80.00"),
                buy_now_price=Decimal("150.00"),
                auction_type=1,
                auction_start_time=now - timedelta(hours=1),
                auction_end_time=now + timedelta(hours=23),
                location="广州市",
                shipping_fee=Decimal("20.00"),
                is_free_shipping=False,
                condition_type=1,
                stock_quantity=1,
                view_count=67,
                bid_count=5,
                favorite_count=18,
                status=2,
                is_featured=True
            ),
            Product(
                id=4,
                seller_id=2,
                category_id=2,
                title="龙鱼 - 金龙血统",
                description="优质金龙鱼，血统纯正，体型完美。适合高端玩家收藏，升值潜力大。",
                images=["https://picsum.photos/400/400?random=dragon1", "https://picsum.photos/400/400?random=dragon2"],
                starting_price=Decimal("2000.00"),
                current_price=Decimal("2500.00"),
                buy_now_price=Decimal("5000.00"),
                auction_type=1,
                auction_start_time=now - timedelta(hours=3),
                auction_end_time=now + timedelta(hours=21),
                location="深圳市",
                shipping_fee=Decimal("100.00"),
                is_free_shipping=False,
                condition_type=1,
                stock_quantity=1,
                view_count=234,
                bid_count=15,
                favorite_count=56,
                status=2,
                is_featured=True
            ),
            # 一口价商品
            Product(
                id=5,
                seller_id=2,
                category_id=3,
                title="智能鱼缸过滤器",
                description="智能过滤系统，自动清洁，静音设计。适合各种尺寸鱼缸，简单易用。",
                images=["https://picsum.photos/400/400?random=filter1", "https://picsum.photos/400/400?random=filter2"],
                starting_price=Decimal("299.00"),
                current_price=Decimal("299.00"),
                buy_now_price=Decimal("299.00"),
                auction_type=2,  # 一口价
                auction_start_time=now - timedelta(days=1),
                auction_end_time=now + timedelta(days=30),
                location="杭州市",
                shipping_fee=Decimal("0.00"),
                is_free_shipping=True,
                condition_type=1,
                stock_quantity=50,
                view_count=123,
                bid_count=0,
                favorite_count=34,
                status=2,
                is_featured=False
            ),
            Product(
                id=6,
                seller_id=2,
                category_id=1,
                title="猫咪玩具套装",
                description="精选猫咪玩具10件套，包含逗猫棒、小老鼠、毛球等。安全材质，增进与猫咪的互动。",
                images=["https://picsum.photos/400/400?random=toy1", "https://picsum.photos/400/400?random=toy2"],
                starting_price=Decimal("89.00"),
                current_price=Decimal("89.00"),
                buy_now_price=Decimal("89.00"),
                auction_type=2,  # 一口价
                auction_start_time=now - timedelta(days=1),
                auction_end_time=now + timedelta(days=30),
                location="成都市",
                shipping_fee=Decimal("0.00"),
                is_free_shipping=True,
                condition_type=1,
                stock_quantity=200,
                view_count=78,
                bid_count=0,
                favorite_count=12,
                status=2,
                is_featured=False
            ),
        ]
        
        for product in products:
            existing = db.query(Product).filter(Product.id == product.id).first()
            if not existing:
                db.add(product)
        
        # 5. 创建专场商品关联
        print("🔗 创建专场商品关联...")
        event_products = [
            # 新春萌宠专场
            EventProduct(event_id=1, product_id=1, sort_order=1),
            EventProduct(event_id=1, product_id=2, sort_order=2),
            # 水族精品专场
            EventProduct(event_id=2, product_id=3, sort_order=1),
            EventProduct(event_id=2, product_id=4, sort_order=2),
            # 一口价精选
            EventProduct(event_id=3, product_id=5, sort_order=1),
            EventProduct(event_id=3, product_id=6, sort_order=2),
        ]
        
        for ep in event_products:
            existing = db.query(EventProduct).filter(
                EventProduct.event_id == ep.event_id,
                EventProduct.product_id == ep.product_id
            ).first()
            if not existing:
                db.add(ep)
        
        # 提交所有更改
        db.commit()
        print("✅ 演示数据创建成功！")
        
        # 显示创建的数据统计
        category_count = db.query(Category).count()
        event_count = db.query(SpecialEvent).count() 
        product_count = db.query(Product).count()
        shop_count = db.query(Shop).count()
        
        print(f"""
📊 数据统计:
- 商品分类: {category_count} 个
- 专场活动: {event_count} 个  
- 商品数量: {product_count} 个
- 商店数量: {shop_count} 个
- 专场商品关联: {len(event_products)} 个
        """)
        
    except Exception as e:
        print(f"❌ 创建数据失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_demo_data()