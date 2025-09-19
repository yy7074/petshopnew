#!/usr/bin/env python3
"""
宠物识别API测试脚本
使用阿里云宠物识别API进行测试
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.services.ai_recognition_service import AIRecognitionService
from app.core.database import get_db

async def test_recognition_api():
    """测试宠物识别API"""
    print("=" * 50)
    print("宠物识别API测试")
    print("=" * 50)
    
    service = AIRecognitionService()
    db = next(get_db())
    
    # 测试用例
    test_cases = [
        {
            "name": "测试狗狗图片URL",
            "image_url": "https://images.dog.ceo/breeds/golden/n02099601_1405.jpg",
            "expected_type": "狗"
        },
        {
            "name": "测试猫咪图片URL", 
            "image_url": "https://cataas.com/cat",
            "expected_type": "猫"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"图片URL: {test_case['image_url']}")
        print("-" * 30)
        
        try:
            result = await service.recognize_pet_image(
                db=db,
                user_id=1,
                image_url=test_case['image_url']
            )
            
            print(f"✅ 识别成功: {result['success']}")
            print(f"📝 消息: {result['message']}")
            
            if result['data']:
                data = result['data']
                print(f"🐾 宠物类型: {data['pet_type']}")
                print(f"🏷️  品种: {data['breed']}")
                print(f"📊 置信度: {data['confidence']:.3f}")
                print(f"🔧 API来源: {result.get('api_source', 'unknown')}")
                
                if data['characteristics']:
                    print(f"✨ 特征: {', '.join(data['characteristics'][:3])}")
                    
                if data.get('estimated_value'):
                    value = data['estimated_value']
                    print(f"💰 估价: ¥{value.get('min_price', 0)} - ¥{value.get('max_price', 0)}")
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_recognition_api())
