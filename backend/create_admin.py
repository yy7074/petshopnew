#!/usr/bin/env python3
"""
创建管理员账号脚本
运行此脚本来创建默认的管理员账号
"""

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.user import User
from app.core.security import get_password_hash
import sys

def create_admin_user():
    """创建管理员账号"""
    db = SessionLocal()
    
    try:
        # 检查是否已存在管理员账号
        existing_admin = db.query(User).filter(User.is_admin == True).first()
        if existing_admin:
            print(f"管理员账号已存在: {existing_admin.username}")
            print("如需重置密码，请手动修改数据库或删除现有管理员账号")
            return
        
        # 默认管理员信息
        admin_data = {
            "username": "admin",
            "phone": "13800138000",
            "email": "admin@petauction.com",
            "password": "admin123456",  # 默认密码
            "nickname": "系统管理员",
            "is_admin": True,
            "is_verified": True,
            "status": 1
        }
        
        # 创建管理员用户
        admin_user = User(
            username=admin_data["username"],
            phone=admin_data["phone"],
            email=admin_data["email"],
            password_hash=get_password_hash(admin_data["password"]),
            nickname=admin_data["nickname"],
            is_admin=admin_data["is_admin"],
            is_verified=admin_data["is_verified"],
            status=admin_data["status"]
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("✅ 管理员账号创建成功!")
        print("=" * 40)
        print(f"用户名: {admin_data['username']}")
        print(f"密码: {admin_data['password']}")
        print(f"邮箱: {admin_data['email']}")
        print(f"手机: {admin_data['phone']}")
        print("=" * 40)
        print("请及时修改默认密码!")
        print("管理后台地址: http://localhost:3000/admin/")
        
    except Exception as e:
        print(f"❌ 创建管理员账号失败: {e}")
        db.rollback()
    finally:
        db.close()

def reset_admin_password():
    """重置管理员密码"""
    db = SessionLocal()
    
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            print("❌ 未找到管理员账号，请先运行创建命令")
            return
        
        new_password = "admin123456"
        admin.password_hash = get_password_hash(new_password)
        db.commit()
        
        print("✅ 管理员密码重置成功!")
        print("=" * 40)
        print(f"用户名: admin")
        print(f"新密码: {new_password}")
        print("=" * 40)
        
    except Exception as e:
        print(f"❌ 重置密码失败: {e}")
        db.rollback()
    finally:
        db.close()

def list_admins():
    """列出所有管理员账号"""
    db = SessionLocal()
    
    try:
        admins = db.query(User).filter(User.is_admin == True).all()
        if not admins:
            print("❌ 未找到任何管理员账号")
            return
        
        print("📋 管理员账号列表:")
        print("=" * 60)
        for admin in admins:
            status_text = "正常" if admin.status == 1 else "冻结" if admin.status == 2 else "禁用"
            print(f"ID: {admin.id}")
            print(f"用户名: {admin.username}")
            print(f"邮箱: {admin.email}")
            print(f"手机: {admin.phone}")
            print(f"状态: {status_text}")
            print(f"创建时间: {admin.created_at}")
            print("-" * 60)
            
    except Exception as e:
        print(f"❌ 获取管理员列表失败: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python create_admin.py create    # 创建管理员账号")
        print("  python create_admin.py reset     # 重置管理员密码")
        print("  python create_admin.py list      # 列出管理员账号")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "create":
        create_admin_user()
    elif command == "reset":
        reset_admin_password()
    elif command == "list":
        list_admins()
    else:
        print("❌ 未知命令，请使用 create、reset 或 list")