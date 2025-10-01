#!/usr/bin/env python3
"""创建测试用户"""

from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

def create_test_user():
    db = SessionLocal()
    
    try:
        # 检查测试用户是否存在
        test_user = db.query(User).filter(User.phone == '13800138000').first()
        
        if test_user:
            # 更新密码
            test_user.password_hash = get_password_hash('test123456')
            print(f"✅ 更新测试用户密码: {test_user.username} / {test_user.phone}")
        else:
            # 创建新用户
            test_user = User(
                username='testuser',
                phone='13800138000',
                password_hash=get_password_hash('test123456'),
                nickname='测试用户',
                status=1
            )
            db.add(test_user)
            print(f"✅ 创建测试用户: testuser / 13800138000")
        
        db.commit()
        print(f"用户ID: {test_user.id}")
        print("登录信息: username=13800138000, password=test123456")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()

