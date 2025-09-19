#!/usr/bin/env python3
"""
初始化同城服务演示数据脚本
"""

import sys
import os
import json
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.core.database import engine, get_db
from app.models.local_service import (
    PetSocialPost, PetSocialComment, PetBreedingInfo, LocalPetStore,
    AquariumDesignService, DoorService, PetValuationService, NearbyItem,
    ServiceStatus
)
from app.models.user import User

def init_demo_data():
    """初始化演示数据"""
    db = Session(bind=engine)
    
    try:
        print("开始初始化同城服务演示数据...")
        
        # 获取现有用户（如果没有用户，先创建一些）
        users = db.query(User).limit(5).all()
        if len(users) < 3:
            print("用户数量不足，请先运行 init_demo_data.py 创建用户数据")
            return
        
        # 1. 创建宠物交流帖子
        social_posts = [
            {
                "user_id": users[0].id,
                "title": "我的金毛宝贝成长记录",
                "content": "分享一下我家金毛从幼犬到成犬的成长过程，希望能帮助到其他宠物主人。金毛真的是很聪明很温顺的狗狗，特别适合家庭饲养。",
                "images": json.dumps(["/static/uploads/golden_puppy.jpg", "/static/uploads/golden_adult.jpg"]),
                "pet_type": "狗",
                "location": "北京市朝阳区",
                "view_count": 156,
                "like_count": 23,
                "comment_count": 8,
                "is_top": True
            },
            {
                "user_id": users[1].id,
                "title": "猫咪训练小技巧分享",
                "content": "很多人说猫咪不能训练，其实是错误的。我家橘猫现在会坐下、握手、转圈，分享一下训练心得。",
                "images": json.dumps(["/static/uploads/cat_training.jpg"]),
                "pet_type": "猫",
                "location": "上海市浦东新区",
                "view_count": 89,
                "like_count": 15,
                "comment_count": 5
            },
            {
                "user_id": users[2].id,
                "title": "兔子饮食注意事项",
                "content": "养兔子的朋友一定要注意饮食搭配，哪些能吃哪些不能吃，这篇帖子详细介绍。",
                "pet_type": "兔子",
                "location": "广州市天河区",
                "view_count": 67,
                "like_count": 12,
                "comment_count": 3
            }
        ]
        
        for post_data in social_posts:
            post = PetSocialPost(**post_data)
            db.add(post)
        
        # 2. 创建宠物配种信息
        breeding_infos = [
            {
                "user_id": users[0].id,
                "pet_name": "球球",
                "pet_type": "狗",
                "breed": "金毛",
                "gender": "公",
                "age": 24,
                "weight": 30.5,
                "health_status": "健康，疫苗齐全",
                "vaccination_status": "已完成全部疫苗接种",
                "images": json.dumps(["/static/uploads/golden_male.jpg"]),
                "description": "纯种金毛，品相优良，性格温顺，已获得多项比赛奖项",
                "requirements": "希望找到同样优秀的母犬配种",
                "location": "北京市朝阳区",
                "contact_phone": "138****5678",
                "contact_wechat": "golden_lover",
                "price": 2000.0,
                "is_available": True
            },
            {
                "user_id": users[1].id,
                "pet_name": "小白",
                "pet_type": "猫",
                "breed": "英短银渐层",
                "gender": "母",
                "age": 18,
                "weight": 4.2,
                "health_status": "健康",
                "vaccination_status": "疫苗齐全",
                "images": json.dumps(["/static/uploads/british_female.jpg"]),
                "description": "纯种英短银渐层，毛色纯正，体型标准",
                "requirements": "寻找品相好的公猫配种",
                "location": "上海市静安区",
                "contact_phone": "139****1234",
                "price": 1500.0,
                "is_available": True
            }
        ]
        
        for breeding_data in breeding_infos:
            breeding = PetBreedingInfo(**breeding_data)
            db.add(breeding)
        
        # 3. 创建本地宠店
        pet_stores = [
            {
                "name": "爱宠天地宠物店",
                "owner_name": "张老板",
                "phone": "010-12345678",
                "address": "北京市朝阳区望京SOHO塔1-2011",
                "latitude": 39.9951,
                "longitude": 116.4722,
                "business_hours": "9:00-21:00",
                "services": json.dumps(["宠物用品", "宠物美容", "宠物寄养", "宠物医疗"]),
                "images": json.dumps(["/static/uploads/petstore1.jpg"]),
                "description": "专业宠物服务连锁店，提供一站式宠物服务",
                "rating": 4.8,
                "review_count": 156,
                "is_verified": True,
                "status": ServiceStatus.ACTIVE
            },
            {
                "name": "萌宠乐园",
                "owner_name": "李经理",
                "phone": "021-87654321",
                "address": "上海市浦东新区陆家嘴金融中心",
                "latitude": 31.2304,
                "longitude": 121.4737,
                "business_hours": "8:30-20:30",
                "services": json.dumps(["宠物用品", "宠物食品", "宠物玩具"]),
                "images": json.dumps(["/static/uploads/petstore2.jpg"]),
                "description": "高端宠物用品专卖店",
                "rating": 4.6,
                "review_count": 89,
                "is_verified": True,
                "status": ServiceStatus.ACTIVE
            }
        ]
        
        for store_data in pet_stores:
            store = LocalPetStore(**store_data)
            db.add(store)
        
        # 4. 创建鱼缸造景服务
        aquarium_services = [
            {
                "provider_id": users[0].id,
                "title": "专业水族造景设计",
                "description": "10年水族造景经验，提供个性化设计方案，包含植物搭配、石材布局、lighting设计等",
                "tank_sizes": json.dumps(["30cm", "60cm", "90cm", "120cm", "定制尺寸"]),
                "design_styles": json.dumps(["自然风", "简约风", "热带风", "海水风"]),
                "price_range": "500-5000元",
                "portfolio_images": json.dumps(["/static/uploads/aquarium1.jpg", "/static/uploads/aquarium2.jpg"]),
                "location": "北京市海淀区",
                "contact_phone": "156****9876",
                "contact_wechat": "aquarium_master",
                "rating": 4.9,
                "order_count": 45,
                "is_available": True
            }
        ]
        
        for service_data in aquarium_services:
            service = AquariumDesignService(**service_data)
            db.add(service)
        
        # 5. 创建上门服务
        door_services = [
            {
                "provider_id": users[1].id,
                "service_name": "宠物美容上门服务",
                "service_type": "美容",
                "description": "专业宠物美容师上门服务，包括洗澡、剪毛、修甲、清耳等",
                "service_area": "北京市三环内",
                "price": 120.0,
                "duration": 90,
                "equipment_needed": "提供专业美容工具和设备",
                "images": json.dumps(["/static/uploads/grooming_service.jpg"]),
                "contact_phone": "187****5432",
                "rating": 4.7,
                "order_count": 78,
                "is_available": True
            },
            {
                "provider_id": users[2].id,
                "service_name": "宠物医疗上门服务",
                "service_type": "医疗",
                "description": "专业兽医上门服务，疫苗接种、健康检查、简单治疗",
                "service_area": "上海市内环内",
                "price": 200.0,
                "duration": 60,
                "equipment_needed": "携带基础医疗设备",
                "images": json.dumps(["/static/uploads/vet_service.jpg"]),
                "contact_phone": "135****8765",
                "rating": 4.9,
                "order_count": 34,
                "is_available": True
            }
        ]
        
        for service_data in door_services:
            service = DoorService(**service_data)
            db.add(service)
        
        # 6. 创建宠物估价记录
        valuations = [
            {
                "user_id": users[0].id,
                "pet_type": "狗",
                "breed": "金毛",
                "age": 24,
                "gender": "公",
                "weight": 30.5,
                "health_status": "健康",
                "special_features": "血统纯正，获得过比赛奖项",
                "images": json.dumps(["/static/uploads/golden_valuation.jpg"]),
                "estimated_value": 8000.0,
                "valuator_id": users[1].id,
                "valuation_notes": "品相优良，血统证书齐全，市场价值较高",
                "status": ServiceStatus.COMPLETED
            }
        ]
        
        for valuation_data in valuations:
            valuation = PetValuationService(**valuation_data)
            db.add(valuation)
        
        # 7. 创建附近发现内容
        nearby_items = [
            {
                "user_id": users[0].id,
                "title": "纯种拉布拉多幼犬出售",
                "description": "2个月大的拉布拉多幼犬，疫苗齐全，品相好，寻找爱心家庭",
                "category": "宠物",
                "price": 3500.0,
                "images": json.dumps(["/static/uploads/labrador_puppy.jpg"]),
                "location": "北京市朝阳区",
                "latitude": 39.9951,
                "longitude": 116.4722,
                "contact_phone": "138****5678",
                "contact_wechat": "lab_breeder",
                "view_count": 89,
                "like_count": 23,
                "is_top": True
            },
            {
                "user_id": users[1].id,
                "title": "猫砂盆转让",
                "description": "全自动智能猫砂盆，9成新，原价1200现价600转让",
                "category": "用品",
                "price": 600.0,
                "images": json.dumps(["/static/uploads/litter_box.jpg"]),
                "location": "上海市浦东新区",
                "latitude": 31.2304,
                "longitude": 121.4737,
                "contact_phone": "139****1234",
                "view_count": 45,
                "like_count": 8
            },
            {
                "user_id": users[2].id,
                "title": "进口狗粮批发",
                "description": "各品牌进口狗粮批发，量大从优，支持同城配送",
                "category": "食品",
                "price": 280.0,
                "images": json.dumps(["/static/uploads/dog_food.jpg"]),
                "location": "广州市天河区",
                "latitude": 23.1291,
                "longitude": 113.2644,
                "contact_phone": "187****5432",
                "view_count": 156,
                "like_count": 34
            }
        ]
        
        for item_data in nearby_items:
            item = NearbyItem(**item_data)
            db.add(item)
        
        # 提交所有数据
        db.commit()
        print("✅ 同城服务演示数据初始化完成！")
        
        # 打印统计信息
        social_count = db.query(PetSocialPost).count()
        breeding_count = db.query(PetBreedingInfo).count()
        store_count = db.query(LocalPetStore).count()
        aquarium_count = db.query(AquariumDesignService).count()
        door_count = db.query(DoorService).count()
        valuation_count = db.query(PetValuationService).count()
        nearby_count = db.query(NearbyItem).count()
        
        print(f"""
📊 数据统计：
- 宠物交流帖子: {social_count} 条
- 宠物配种信息: {breeding_count} 条
- 本地宠店: {store_count} 家
- 鱼缸造景服务: {aquarium_count} 个
- 上门服务: {door_count} 个
- 宠物估价记录: {valuation_count} 条
- 附近发现: {nearby_count} 条
        """)
        
    except Exception as e:
        print(f"❌ 初始化失败: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

def clear_demo_data():
    """清除演示数据"""
    db = Session(bind=engine)
    
    try:
        print("开始清除同城服务演示数据...")
        
        # 删除所有同城服务相关数据
        db.query(PetSocialComment).delete()
        db.query(PetSocialPost).delete()
        db.query(PetBreedingInfo).delete()
        db.query(LocalPetStore).delete()
        db.query(AquariumDesignService).delete()
        db.query(DoorService).delete()
        db.query(PetValuationService).delete()
        db.query(NearbyItem).delete()
        
        db.commit()
        print("✅ 同城服务演示数据清除完成！")
        
    except Exception as e:
        print(f"❌ 清除失败: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="同城服务演示数据管理")
    parser.add_argument("action", choices=["init", "clear"], help="操作类型: init(初始化) 或 clear(清除)")
    
    args = parser.parse_args()
    
    if args.action == "init":
        init_demo_data()
    elif args.action == "clear":
        clear_demo_data()

