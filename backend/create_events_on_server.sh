#!/bin/bash
# 在远程服务器上创建专场活动

echo "🚀 连接到远程服务器并创建专场活动..."

ssh root@39.96.177.57 << 'ENDSSH'

# 创建Python脚本
cat > /tmp/create_events.py << 'ENDPYTHON'
import pymysql
from datetime import datetime, timedelta

try:
    print("🎯 连接数据库...")
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='123456',
        database='petshop_auction',
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    
    print("✅ 连接成功！")
    print("🗑️  清除旧数据...")
    
    # 清除旧数据
    cursor.execute("DELETE FROM event_products")
    cursor.execute("DELETE FROM special_events")
    conn.commit()
    
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
            'is_active': 1,
        },
        {
            'id': 2,
            'title': '水族精品专场',
            'description': '精品观赏鱼和水族用品，打造完美水族世界',
            'banner_image': '/static/uploads/event2.jpg',
            'start_time': now - timedelta(hours=12),
            'end_time': now + timedelta(days=25),
            'is_active': 1,
        },
        {
            'id': 3,
            'title': '一口价精选',
            'description': '精选优质商品，一口价直接购买，无需等待',
            'banner_image': '/static/uploads/event3.jpg',
            'start_time': now - timedelta(days=2),
            'end_time': now + timedelta(days=60),
            'is_active': 1,
        },
        {
            'id': 4,
            'title': '爬宠专区',
            'description': '各类爬行宠物及用品专场',
            'banner_image': '/static/uploads/event4.jpg',
            'start_time': now,
            'end_time': now + timedelta(days=15),
            'is_active': 1,
        },
    ]
    
    print("\n📦 创建专场活动...")
    for event in events:
        sql = """
            INSERT INTO special_events 
            (id, title, description, banner_image, start_time, end_time, is_active, created_at)
            VALUES 
            (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            event['id'],
            event['title'],
            event['description'],
            event['banner_image'],
            event['start_time'],
            event['end_time'],
            event['is_active'],
            now
        ))
        print(f"✅ {event['title']}")
    
    conn.commit()
    
    # 验证
    cursor.execute("SELECT COUNT(*) FROM special_events")
    count = cursor.fetchone()[0]
    print(f"\n🎉 成功创建 {count} 个专场活动！")
    
    # 显示列表
    cursor.execute("""
        SELECT id, title, 
               DATE_FORMAT(start_time, '%Y-%m-%d %H:%i') as start_time,
               DATE_FORMAT(end_time, '%Y-%m-%d %H:%i') as end_time,
               is_active 
        FROM special_events ORDER BY id
    """)
    
    print("\n📋 专场活动列表:")
    print("-" * 80)
    for row in cursor.fetchall():
        status = "🟢 进行中" if row[4] else "🔴 已结束"
        print(f"ID: {row[0]} | {row[1]}")
        print(f"   时间: {row[2]} ~ {row[3]} | {status}")
        print("-" * 80)
    
    cursor.close()
    conn.close()
    print("\n✅ 所有操作完成！")
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()

ENDPYTHON

# 执行Python脚本
echo "执行创建专场活动脚本..."
python3 /tmp/create_events.py

# 清理临时文件
rm /tmp/create_events.py

echo "✅ 完成！"

ENDSSH

echo ""
echo "🎯 验证专场活动..."
curl -s "http://39.96.177.57:3000/api/v1/events/" | python3 -m json.tool | head -30

