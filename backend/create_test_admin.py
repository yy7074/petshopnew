#!/usr/bin/env python3
"""创建测试管理员"""

from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

def create_test_admin():
    db = SessionLocal()
    
    try:
        # 检查管理员是否存在
        admin_user = db.query(User).filter(User.phone == '18888888888').first()
        
        if admin_user:
            # 更新密码和管理员权限
            admin_user.password_hash = get_password_hash('admin123')
            admin_user.is_admin = True
            admin_user.status = 1
            print(f"✅ 更新管理员账号: {admin_user.username} / {admin_user.phone}")
        else:
            # 创建新管理员
            admin_user = User(
                username='admin',
                phone='18888888888',
                password_hash=get_password_hash('admin123'),
                nickname='系统管理员',
                is_admin=True,
                status=1
            )
            db.add(admin_user)
            print(f"✅ 创建管理员账号: admin / 18888888888")
        
        db.commit()
        print(f"管理员ID: {admin_user.id}")
        print(f"is_admin: {admin_user.is_admin}")
        print("登录信息: username=18888888888, password=admin123")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_admin()

