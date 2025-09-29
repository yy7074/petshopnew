#!/usr/bin/env python3
"""
创建启动广告演示数据
"""

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.splash_ad import SplashAd, AdType, AdStatus
from datetime import datetime, timedelta

def create_demo_splash_ads():
    """创建演示启动广告数据"""
    
    # 创建数据库表
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # 检查是否已有数据
        existing_count = db.query(SplashAd).count()
        if existing_count > 0:
            print(f"已存在 {existing_count} 个启动广告，跳过创建演示数据")
            return
        
        # 创建演示广告数据
        demo_ads = [
            {
                "title": "欢迎来到拍宠有道！",
                "description": "发现更多可爱宠物，参与精彩拍卖",
                "ad_type": AdType.IMAGE,
                "image_url": "/static/uploads/splash_ads/welcome_ad.jpg",
                "click_action": "none",
                "display_duration": 3,
                "skip_enabled": True,
                "skip_delay": 1,
                "status": AdStatus.ACTIVE,
                "priority": 10,
                "weight": 5,
                "start_time": datetime.now(),
                "end_time": datetime.now() + timedelta(days=30)
            },
            {
                "title": "新用户专享优惠",
                "description": "注册即送100元代金券，快来体验吧！",
                "ad_type": AdType.IMAGE,
                "image_url": "/static/uploads/splash_ads/newuser_promo.jpg",
                "click_action": "url",
                "target_url": "/register",
                "display_duration": 4,
                "skip_enabled": True,
                "skip_delay": 2,
                "status": AdStatus.ACTIVE,
                "priority": 8,
                "weight": 3,
                "start_time": datetime.now(),
                "end_time": datetime.now() + timedelta(days=7)
            },
            {
                "title": "精品宠物拍卖",
                "description": "每日精选优质宠物，限时拍卖中",
                "ad_type": AdType.IMAGE,
                "image_url": "/static/uploads/splash_ads/auction_pets.jpg",
                "click_action": "category",
                "target_id": 1,  # 宠物分类ID
                "display_duration": 5,
                "skip_enabled": True,
                "skip_delay": 0,
                "status": AdStatus.ACTIVE,
                "priority": 5,
                "weight": 2,
                "start_time": datetime.now(),
                "end_time": datetime.now() + timedelta(days=15)
            },
            {
                "title": "春季宠物用品大促",
                "description": "全场宠物用品5折起，限时抢购",
                "ad_type": AdType.IMAGE,
                "image_url": "/static/uploads/splash_ads/spring_sale.jpg",
                "click_action": "url",
                "target_url": "/products?category=supplies",
                "display_duration": 3,
                "skip_enabled": True,
                "skip_delay": 1,
                "status": AdStatus.INACTIVE,  # 暂停状态
                "priority": 3,
                "weight": 1,
                "start_time": datetime.now() + timedelta(days=1),
                "end_time": datetime.now() + timedelta(days=10)
            },
            {
                "title": "宠物健康知识分享",
                "description": "专业兽医在线答疑，免费咨询",
                "ad_type": AdType.IMAGE,
                "image_url": "/static/uploads/splash_ads/health_tips.jpg",
                "click_action": "url",
                "target_url": "/health-tips",
                "display_duration": 4,
                "skip_enabled": True,
                "skip_delay": 2,
                "status": AdStatus.DRAFT,  # 草稿状态
                "priority": 1,
                "weight": 1
            }
        ]
        
        # 插入数据
        for ad_data in demo_ads:
            ad = SplashAd(**ad_data)
            db.add(ad)
        
        db.commit()
        
        print(f"✅ 成功创建 {len(demo_ads)} 个演示启动广告")
        print("\n广告列表:")
        
        # 显示创建的广告
        ads = db.query(SplashAd).all()
        for ad in ads:
            print(f"- ID: {ad.id}, 标题: {ad.title}, 状态: {ad.status.value}, 优先级: {ad.priority}")
        
        print(f"\n📱 客户端API测试:")
        print(f"curl http://localhost:3000/api/v1/app/splash-ad")
        
        print(f"\n🔧 后台管理:")
        print(f"访问: http://localhost:3000/admin")
        print(f"或: https://catdog.dachaonet.com/admin")
        
    except Exception as e:
        print(f"❌ 创建演示数据失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 创建启动广告演示数据")
    print("=" * 50)
    create_demo_splash_ads()
    print("\n🎉 演示数据创建完成!")
