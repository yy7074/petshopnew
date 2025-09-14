#!/usr/bin/env python3
"""
同城服务演示数据初始化脚本
"""

import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.local_service import LocalServicePost, PetSocialPost
from app.models.user import User

def create_local_service_demo_data():
    """创建同城服务演示数据"""
    db = SessionLocal()
    
    try:
        print("🚀 开始创建同城服务演示数据...")
        
        # 使用现有用户
        test_user = db.query(User).first()
        if not test_user:
            print("❌ 没有找到用户，请先运行 init_demo_data.py 创建用户")
            return
        print(f"✅ 使用现有用户: {test_user.username}")

        # 1. 创建宠物交流帖子
        print("📝 创建宠物交流帖子...")
        pet_posts = [
            PetSocialPost(
                user_id=test_user.id,
                title="我家金毛的训练心得分享",
                content="经过三个月的训练，我家金毛终于学会了基本指令。分享一些训练技巧给大家...",
                images=["https://picsum.photos/400/300?random=1001", "https://picsum.photos/400/300?random=1002"],
                pet_type="狗狗",
                pet_breed="金毛寻回犬",
                pet_age="1岁",
                pet_gender="公",
                city="北京",
                district="朝阳区",
                category="experience",
                tags=["训练", "金毛", "经验分享"],
                view_count=156,
                like_count=23,
                comment_count=8
            ),
            PetSocialPost(
                user_id=test_user.id,
                title="求助：猫咪不爱喝水怎么办？",
                content="我家猫咪最近不爱喝水，很担心它的健康。有经验的朋友能给点建议吗？",
                images=["https://picsum.photos/400/300?random=1003"],
                pet_type="猫咪",
                pet_breed="英短蓝猫",
                pet_age="2岁",
                pet_gender="母",
                city="上海",
                district="浦东新区",
                category="question",
                tags=["猫咪", "健康", "求助"],
                view_count=89,
                like_count=12,
                comment_count=15
            ),
            PetSocialPost(
                user_id=test_user.id,
                title="晒晒我家的小仓鼠",
                content="我家小仓鼠太可爱了！每天都要拍好多照片 🐹",
                images=["https://picsum.photos/400/300?random=1004", "https://picsum.photos/400/300?random=1005"],
                pet_type="小宠",
                pet_breed="仓鼠",
                pet_age="6个月",
                city="广州",
                district="天河区",
                category="show",
                tags=["仓鼠", "可爱", "晒宠"],
                view_count=234,
                like_count=45,
                comment_count=12
            )
        ]
        
        for post in pet_posts:
            db.add(post)
        
        # 2. 创建本地宠店服务
        print("🏪 创建本地宠店服务...")
        local_stores = [
            LocalServicePost(
                user_id=test_user.id,
                service_type="local_store",
                title="萌宠天地 - 专业宠物用品店",
                description="提供各类宠物用品、食品和玩具，品质保证，价格实惠",
                content="我们是一家专业的宠物用品店，经营各种宠物食品、玩具、用品等。店内商品齐全，价格合理，欢迎各位宠物主人前来选购！",
                province="北京市",
                city="北京",
                district="朝阳区",
                address="朝阳区三里屯SOHO A座1001",
                price=Decimal("0.00"),
                contact_name="张老板",
                contact_phone="13800138001",
                images=["https://picsum.photos/400/300?random=2001", "https://picsum.photos/400/300?random=2002"],
                tags=["宠物用品", "食品", "玩具", "专业"],
                view_count=456,
                like_count=32,
                comment_count=8
            ),
            LocalServicePost(
                user_id=test_user.id,
                service_type="local_store",
                title="爱宠医院 - 24小时宠物医疗",
                description="专业宠物医疗服务，24小时急诊，经验丰富的兽医团队",
                content="本院拥有先进的医疗设备和经验丰富的兽医团队，提供宠物体检、疫苗接种、疾病治疗等全方位医疗服务。",
                province="上海市",
                city="上海",
                district="浦东新区",
                address="浦东新区陆家嘴金融中心B座",
                price=Decimal("100.00"),
                price_unit="起",
                contact_name="李医生",
                contact_phone="13800138002",
                images=["https://picsum.photos/400/300?random=2003", "https://picsum.photos/400/300?random=2004"],
                tags=["宠物医院", "24小时", "专业医疗"],
                view_count=789,
                like_count=56,
                comment_count=23
            )
        ]
        
        for store in local_stores:
            db.add(store)
        
        # 3. 创建鱼缸造景服务
        print("🐠 创建鱼缸造景服务...")
        aquarium_services = [
            LocalServicePost(
                user_id=test_user.id,
                service_type="aquarium_design",
                title="专业水族造景设计",
                description="提供个性化水族箱造景设计，从设计到施工一站式服务",
                content="我们是专业的水族造景团队，拥有多年的设计和施工经验。可以根据客户需求设计各种风格的水族景观，包括自然风、现代简约风等。",
                province="广东省",
                city="深圳",
                district="南山区",
                address="南山区科技园创业大厦",
                price=Decimal("500.00"),
                price_unit="起",
                contact_name="王师傅",
                contact_phone="13800138003",
                images=["https://picsum.photos/400/300?random=3001", "https://picsum.photos/400/300?random=3002"],
                tags=["水族造景", "专业设计", "一站式服务"],
                view_count=345,
                like_count=28,
                comment_count=12
            ),
            LocalServicePost(
                user_id=test_user.id,
                service_type="aquarium_design",
                title="海水缸定制服务",
                description="专业海水缸设计定制，珊瑚造景，系统维护",
                content="专业海水缸定制服务，包括系统设计、设备选型、珊瑚造景、后期维护等全套服务。",
                province="浙江省",
                city="杭州",
                district="西湖区",
                address="西湖区文二路海外海大厦",
                price=Decimal("2000.00"),
                price_unit="起",
                contact_name="陈师傅",
                contact_phone="13800138004",
                images=["https://picsum.photos/400/300?random=3003", "https://picsum.photos/400/300?random=3004"],
                tags=["海水缸", "珊瑚", "定制服务"],
                view_count=234,
                like_count=19,
                comment_count=6
            )
        ]
        
        for service in aquarium_services:
            db.add(service)
        
        # 4. 创建上门服务
        print("🚪 创建上门服务...")
        door_services = [
            LocalServicePost(
                user_id=test_user.id,
                service_type="door_service",
                title="宠物上门洗澡美容服务",
                description="专业宠物美容师上门服务，让您的爱宠在家享受专业护理",
                content="我们提供专业的宠物上门洗澡美容服务，美容师经验丰富，设备齐全，让您的爱宠在熟悉的环境中享受专业护理。",
                province="北京市",
                city="北京",
                district="海淀区",
                address="服务范围：五环内",
                price=Decimal("80.00"),
                price_unit="次",
                contact_name="美容师小李",
                contact_phone="13800138005",
                images=["https://picsum.photos/400/300?random=4001", "https://picsum.photos/400/300?random=4002"],
                tags=["上门服务", "宠物美容", "专业"],
                view_count=567,
                like_count=45,
                comment_count=18
            ),
            LocalServicePost(
                user_id=test_user.id,
                service_type="door_service",
                title="宠物上门训练服务",
                description="专业训犬师上门训练，纠正行为问题，建立良好习惯",
                content="专业训犬师提供上门训练服务，包括基础服从训练、行为纠正、社会化训练等。",
                province="上海市",
                city="上海",
                district="徐汇区",
                address="服务范围：内环内",
                price=Decimal("150.00"),
                price_unit="次",
                contact_name="训犬师老王",
                contact_phone="13800138006",
                images=["https://picsum.photos/400/300?random=4003", "https://picsum.photos/400/300?random=4004"],
                tags=["上门训练", "行为纠正", "专业训犬师"],
                view_count=432,
                like_count=38,
                comment_count=14
            )
        ]
        
        for service in door_services:
            db.add(service)
        
        db.commit()
        
        print("✅ 同城服务演示数据创建成功！")
        print(f"📊 数据统计:")
        print(f"- 宠物交流帖子: 3 个")
        print(f"- 本地宠店服务: 2 个")
        print(f"- 鱼缸造景服务: 2 个")
        print(f"- 上门服务: 2 个")
        print(f"- 总计服务: 9 个")
        
    except Exception as e:
        print(f"❌ 创建演示数据失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_local_service_demo_data()
