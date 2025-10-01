#!/usr/bin/env python3
"""
在远程服务器上创建专场活动数据
"""
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 远程数据库配置
REMOTE_DB_URL = "mysql+pymysql://root:123456@39.96.177.57:3306/petshop_auction"

def create_special_events():
    """创建专场活动数据"""
    try:
        print("🎯 连接远程数据库...")
        engine = create_engine(REMOTE_DB_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        print("✅ 连接成功！")
        print("🗑️  清除旧数据...")
        
        # 清除旧数据
        session.execute(text("DELETE FROM event_products"))
        session.execute(text("DELETE FROM special_events"))
        session.commit()
        
        # 创建专场数据
        now = datetime.now()
        events = [
            {
                'id': 1,
                'title': '新春萌宠专场',
                'description': '新春特惠，精选优质宠物，限时拍卖！',
                'banner_image': '/static/uploads/event1.jpg',
                'start_time': now - timedelta(days=1),
                'end_time': now + timedelta(days=30),
                'is_active': True,
                'created_at': now
            },
            {
                'id': 2,
                'title': '水族精品专场',
                'description': '精品观赏鱼和水族用品，打造完美水族世界',
                'banner_image': '/static/uploads/event2.jpg',
                'start_time': now - timedelta(hours=12),
                'end_time': now + timedelta(days=25),
                'is_active': True,
                'created_at': now
            },
            {
                'id': 3,
                'title': '一口价精选',
                'description': '精选优质商品，一口价直接购买，无需等待',
                'banner_image': '/static/uploads/event3.jpg',
                'start_time': now - timedelta(days=2),
                'end_time': now + timedelta(days=60),
                'is_active': True,
                'created_at': now
            },
            {
                'id': 4,
                'title': '爬宠专区',
                'description': '各类爬行宠物及用品专场',
                'banner_image': '/static/uploads/event4.jpg',
                'start_time': now,
                'end_time': now + timedelta(days=15),
                'is_active': True,
                'created_at': now
            },
        ]
        
        print("\n📦 创建专场活动...")
        for event in events:
            sql = text("""
                INSERT INTO special_events 
                (id, title, description, banner_image, start_time, end_time, is_active, created_at)
                VALUES 
                (:id, :title, :description, :banner_image, :start_time, :end_time, :is_active, :created_at)
            """)
            session.execute(sql, event)
            print(f"✅ {event['title']}")
        
        session.commit()
        
        # 验证
        result = session.execute(text("SELECT COUNT(*) FROM special_events"))
        count = result.scalar()
        print(f"\n🎉 成功创建 {count} 个专场活动！")
        
        # 显示列表
        result = session.execute(text("""
            SELECT id, title, 
                   DATE_FORMAT(start_time, '%Y-%m-%d %H:%i') as start_time,
                   DATE_FORMAT(end_time, '%Y-%m-%d %H:%i') as end_time,
                   is_active 
            FROM special_events ORDER BY id
        """))
        
        print("\n📋 专场活动列表:")
        print("-" * 80)
        for row in result:
            status = "🟢 进行中" if row[4] else "🔴 已结束"
            print(f"ID: {row[0]} | {row[1]}")
            print(f"   时间: {row[2]} ~ {row[3]} | {status}")
            print("-" * 80)
        
        session.close()
        print("\n✅ 所有操作完成！")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 在远程服务器创建专场活动")
    print("=" * 80)
    create_special_events()

