"""
初始化店铺申请演示数据
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.user import User
from app.models.store_application import StoreApplication
from app.core.security import get_password_hash
from datetime import datetime
from decimal import Decimal

def init_demo_data():
    """初始化演示数据"""
    db: Session = SessionLocal()
    
    try:
        print("开始初始化店铺申请演示数据...")
        
        # 创建管理员用户
        admin_user = db.query(User).filter(User.phone == "13800138000").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                phone="13800138000",
                email="admin@petauction.com",
                password_hash=get_password_hash("admin123"),
                nickname="管理员",
                real_name="系统管理员",
                is_admin=True,
                is_verified=True,
                status=1
            )
            db.add(admin_user)
            print("✓ 创建管理员用户")
        
        # 创建测试用户
        test_user = db.query(User).filter(User.phone == "13800138001").first()
        if not test_user:
            test_user = User(
                username="testuser",
                phone="13800138001",
                email="test@example.com",
                password_hash=get_password_hash("123456"),
                nickname="测试用户",
                real_name="张三",
                is_verified=True,
                status=1
            )
            db.add(test_user)
            print("✓ 创建测试用户")
        
        db.commit()
        
        # 创建示例店铺申请
        existing_application = db.query(StoreApplication).filter(
            StoreApplication.user_id == test_user.id
        ).first()
        
        if not existing_application:
            demo_application = StoreApplication(
                user_id=test_user.id,
                store_name="萌宠小屋",
                store_description="专业的宠物用品和宠物服务，为您的爱宠提供最好的照顾。",
                store_type="个人店",
                consignee_name="张三",
                consignee_phone="13800138001",
                return_region="山东省济南市历下区",
                return_address="经十路123号",
                real_name="张三",
                id_number="370102199001011234",
                id_start_date="2010-01-01",
                id_end_date="2030-01-01",
                id_front_image="/static/uploads/store_applications/demo_id_front.jpg",
                id_back_image="/static/uploads/store_applications/demo_id_back.jpg",
                deposit_amount=Decimal('600.00'),
                annual_fee=Decimal('188.00'),
                status=0  # 待审核
            )
            db.add(demo_application)
            print("✓ 创建示例店铺申请")
        
        db.commit()
        print("演示数据初始化完成！")
        
        print("\n登录信息:")
        print("管理员账号: 13800138000 / admin123")
        print("测试用户账号: 13800138001 / 123456")
        print("\n可以使用测试用户账号登录查看开店申请状态")
        
    except Exception as e:
        print(f"初始化失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_demo_data()
