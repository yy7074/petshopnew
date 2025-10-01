#!/usr/bin/env python3
"""
创建专场活动演示数据
"""
import os
import sys
from datetime import datetime, timedelta

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 使用已安装的包
try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    import pymysql
except ImportError as e:
    print(f"❌ 缺少必要的包: {e}")
    print("请确保已安装: pymysql, sqlalchemy")
    sys.exit(1)

# 数据库配置（使用本地数据库）
DATABASE_URL = "mysql+pymysql://root:123456@localhost:3306/petshop_auction"

def create_special_events():
    """创建专场活动数据"""
    try:
        # 创建数据库连接
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        print("🎯 开始创建专场活动数据...")
        
        # 检查表是否存在
        result = session.execute(text("SHOW TABLES LIKE 'special_events'"))
        if not result.fetchone():
            print("❌ special_events 表不存在")
            return
        
        # 清除现有数据（可选）
        session.execute(text("DELETE FROM special_events"))
        session.commit()
        print("🗑️  清除了旧的专场数据")
        
        # 创建专场数据
        now = datetime.now()
        events = [
            {
                'id': 1,
                'title': '新春萌宠专场',
                'description': '新春特惠，精选优质宠物，限时拍卖！',
                'banner_image': 'https://picsum.photos/800/400?random=event1',
                'start_time': now - timedelta(days=1),
                'end_time': now + timedelta(days=7),
                'is_active': True,
                'created_at': now
            },
            {
                'id': 2,
                'title': '水族精品专场',
                'description': '精品观赏鱼和水族用品，打造完美水族世界',
                'banner_image': 'https://picsum.photos/800/400?random=event2',
                'start_time': now - timedelta(hours=12),
                'end_time': now + timedelta(days=5),
                'is_active': True,
                'created_at': now
            },
            {
                'id': 3,
                'title': '一口价精选',
                'description': '精选优质商品，一口价直接购买，无需等待',
                'banner_image': 'https://picsum.photos/800/400?random=event3',
                'start_time': now - timedelta(days=2),
                'end_time': now + timedelta(days=10),
                'is_active': True,
                'created_at': now
            },
        ]
        
        # 插入数据
        for event in events:
            sql = text("""
                INSERT INTO special_events 
                (id, title, description, banner_image, start_time, end_time, is_active, created_at)
                VALUES 
                (:id, :title, :description, :banner_image, :start_time, :end_time, :is_active, :created_at)
            """)
            session.execute(sql, event)
            print(f"✅ 创建专场: {event['title']}")
        
        session.commit()
        print("\n🎉 专场活动数据创建成功！")
        
        # 验证数据
        result = session.execute(text("SELECT COUNT(*) FROM special_events"))
        count = result.scalar()
        print(f"📊 当前专场数量: {count}")
        
        # 显示创建的专场
        result = session.execute(text("SELECT id, title, is_active FROM special_events"))
        print("\n📋 专场列表:")
        for row in result:
            status = "✅ 激活" if row[2] else "❌ 未激活"
            print(f"  {row[0]}. {row[1]} - {status}")
        
        session.close()
        
    except Exception as e:
        print(f"❌ 创建专场数据失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 创建专场活动演示数据")
    print("=" * 50)
    create_special_events()
