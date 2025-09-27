#!/usr/bin/env python3
"""
创建测试账号脚本
手机号：18888888888
密码：111111
"""

import asyncio
import sys
from sqlalchemy.orm import sessionmaker
from app.core.database import engine
from app.models.user import User
from app.core.security import get_password_hash

async def create_test_account():
    """创建测试账号"""
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # 检查账号是否已存在
        existing_user = db.query(User).filter(
            (User.phone == "18888888888") | (User.username == "18888888888")
        ).first()
        
        if existing_user:
            print("测试账号已存在:")
            print(f"ID: {existing_user.id}")
            print(f"用户名: {existing_user.username}")
            print(f"手机号: {existing_user.phone}")
            print(f"昵称: {existing_user.nickname}")
            print(f"状态: {existing_user.status}")
            return existing_user
        
        # 创建测试账号
        hashed_password = get_password_hash("111111")
        
        test_user = User(
            username="18888888888",
            phone="18888888888",
            nickname="测试用户",
            password_hash=hashed_password,
            is_verified=True,
            is_seller=True,  # 设置为卖家，可以发布商品
        )
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        print("测试账号创建成功:")
        print(f"ID: {test_user.id}")
        print(f"用户名: {test_user.username}")
        print(f"手机号: {test_user.phone}")
        print(f"昵称: {test_user.nickname}")
        print(f"密码: 111111")
        print(f"状态: {test_user.status}")
        print(f"是否卖家: {test_user.is_seller}")
        
        return test_user
        
    except Exception as e:
        db.rollback()
        print(f"创建测试账号失败: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(create_test_account())
