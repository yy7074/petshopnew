#!/usr/bin/env python3
"""
启动广告功能测试脚本
"""

import requests
import json
from datetime import datetime

# 配置
BASE_URL = "http://localhost:3000/api/v1"
ADMIN_TOKEN = "admin-token"  # 开发环境使用的简单token

def test_client_splash_ad():
    """测试客户端获取启动广告API"""
    print("🧪 测试客户端获取启动广告...")
    
    try:
        response = requests.get(f"{BASE_URL}/app/splash-ad")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data:
                print("✅ 成功获取启动广告:")
                print(f"   - ID: {data['id']}")
                print(f"   - 类型: {data['ad_type']}")
                print(f"   - 显示时长: {data['display_duration']}秒")
                print(f"   - 允许跳过: {data['skip_enabled']}")
                return data['id']
            else:
                print("⚠️  当前没有有效的启动广告")
                return None
        else:
            print(f"❌ 请求失败: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return None

def test_admin_splash_ads():
    """测试管理员获取启动广告列表API"""
    print("\n🧪 测试管理员获取启动广告列表...")
    
    headers = {
        "Authorization": f"Bearer {ADMIN_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/splash-ads", headers=headers)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 成功获取广告列表:")
            print(f"   - 总数: {data['total']}")
            print(f"   - 当前页: {data['page']}")
            print(f"   - 每页数量: {data['page_size']}")
            
            if data['items']:
                print("   - 广告列表:")
                for ad in data['items']:
                    print(f"     * ID: {ad['id']}, 标题: {ad['title']}, 状态: {ad['status']}")
            
            return True
        else:
            print(f"❌ 请求失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_create_splash_ad():
    """测试创建启动广告"""
    print("\n🧪 测试创建启动广告...")
    
    headers = {
        "Authorization": f"Bearer {ADMIN_TOKEN}",
        "Content-Type": "application/json"
    }
    
    ad_data = {
        "title": "测试广告 - " + datetime.now().strftime("%H:%M:%S"),
        "description": "这是一个测试广告",
        "ad_type": "image",
        "image_url": "/static/uploads/splash_ads/test_ad.jpg",
        "click_action": "none",
        "display_duration": 3,
        "skip_enabled": True,
        "skip_delay": 1,
        "priority": 1,
        "weight": 1
    }
    
    try:
        response = requests.post(f"{BASE_URL}/splash-ads", headers=headers, json=ad_data)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 成功创建广告:")
            print(f"   - ID: {data['id']}")
            print(f"   - 标题: {data['title']}")
            print(f"   - 状态: {data['status']}")
            return data['id']
        else:
            print(f"❌ 创建失败: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return None

def test_update_ad_stats(ad_id):
    """测试更新广告统计"""
    if not ad_id:
        print("\n⚠️  跳过统计测试（没有有效的广告ID）")
        return
    
    print(f"\n🧪 测试更新广告统计 (ID: {ad_id})...")
    
    # 测试展示统计
    try:
        response = requests.post(f"{BASE_URL}/app/splash-ad/{ad_id}/stats", 
                                json={"action": "view"})
        print(f"展示统计 - 状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 展示统计更新成功")
        else:
            print(f"❌ 展示统计更新失败: {response.text}")
    except Exception as e:
        print(f"❌ 展示统计请求异常: {e}")
    
    # 测试点击统计
    try:
        response = requests.post(f"{BASE_URL}/app/splash-ad/{ad_id}/stats", 
                                json={"action": "click"})
        print(f"点击统计 - 状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 点击统计更新成功")
        else:
            print(f"❌ 点击统计更新失败: {response.text}")
    except Exception as e:
        print(f"❌ 点击统计请求异常: {e}")

def test_backend_health():
    """测试后端服务健康状态"""
    print("🧪 测试后端服务健康状态...")
    
    try:
        response = requests.get("http://localhost:3000/health")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 服务正常: {data.get('message', '')}")
            return True
        else:
            print(f"❌ 服务异常: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        print("请确保后端服务正在运行: python main.py")
        return False

def main():
    """主测试流程"""
    print("🚀 启动广告功能完整测试")
    print("=" * 60)
    
    # 1. 测试后端服务
    if not test_backend_health():
        print("\n❌ 后端服务不可用，测试终止")
        return
    
    # 2. 测试客户端API
    ad_id = test_client_splash_ad()
    
    # 3. 测试管理员API
    admin_success = test_admin_splash_ads()
    
    # 4. 测试创建广告
    new_ad_id = test_create_splash_ad()
    
    # 5. 测试统计更新
    test_ad_id = ad_id or new_ad_id
    test_update_ad_stats(test_ad_id)
    
    # 测试结果总结
    print("\n" + "=" * 60)
    print("🎉 测试完成！")
    print("\n📋 测试结果:")
    print(f"   - 后端服务: ✅ 正常")
    print(f"   - 客户端API: {'✅ 正常' if ad_id else '⚠️  无广告'}")
    print(f"   - 管理员API: {'✅ 正常' if admin_success else '❌ 异常'}")
    print(f"   - 创建广告: {'✅ 成功' if new_ad_id else '❌ 失败'}")
    print(f"   - 统计更新: {'✅ 测试完成' if test_ad_id else '⚠️  跳过'}")
    
    print(f"\n🔗 访问地址:")
    print(f"   - API文档: http://localhost:3000/docs")
    print(f"   - 后台管理: http://localhost:3000/admin")
    print(f"   - 或线上: https://catdog.dachaonet.com/admin")

if __name__ == "__main__":
    main()
