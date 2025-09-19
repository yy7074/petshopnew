#!/usr/bin/env python3
"""
测试同城服务API脚本
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"

def test_api():
    """测试同城服务API"""
    print("🧪 开始测试同城服务API...")
    
    # 测试API列表
    test_cases = [
        {
            "name": "获取宠物交流帖子",
            "method": "GET",
            "url": f"{BASE_URL}/local-services/social-posts",
            "params": {"page": 1, "page_size": 10}
        },
        {
            "name": "获取宠物配种信息",
            "method": "GET", 
            "url": f"{BASE_URL}/local-services/breeding-info",
            "params": {"page": 1, "page_size": 10}
        },
        {
            "name": "获取本地宠店",
            "method": "GET",
            "url": f"{BASE_URL}/local-services/pet-stores", 
            "params": {"page": 1, "page_size": 10}
        },
        {
            "name": "获取鱼缸造景服务",
            "method": "GET",
            "url": f"{BASE_URL}/local-services/aquarium-design",
            "params": {"page": 1, "page_size": 10}
        },
        {
            "name": "获取上门服务",
            "method": "GET",
            "url": f"{BASE_URL}/local-services/door-services",
            "params": {"page": 1, "page_size": 10}
        },
        {
            "name": "获取同城快取",
            "method": "GET",
            "url": f"{BASE_URL}/local-services/pickup-services",
            "params": {"page": 1, "page_size": 10}
        },
        {
            "name": "获取附近发现",
            "method": "GET",
            "url": f"{BASE_URL}/local-services/nearby-items",
            "params": {"page": 1, "page_size": 10}
        },
        {
            "name": "获取服务统计",
            "method": "GET",
            "url": f"{BASE_URL}/local-services/stats"
        }
    ]
    
    results = []
    
    for test in test_cases:
        try:
            print(f"\n🔍 测试: {test['name']}")
            
            if test['method'] == 'GET':
                response = requests.get(test['url'], params=test.get('params', {}), timeout=10)
            else:
                response = requests.post(test['url'], json=test.get('data', {}), timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 成功 - 状态码: {response.status_code}")
                
                # 打印简要信息
                if 'items' in data:
                    print(f"   📊 返回 {len(data['items'])} 条记录")
                    if 'total' in data:
                        print(f"   📈 总计 {data['total']} 条记录")
                elif isinstance(data, dict):
                    print(f"   📋 返回数据字段: {list(data.keys())}")
                
                results.append({
                    "test": test['name'],
                    "status": "SUCCESS",
                    "status_code": response.status_code,
                    "data_size": len(data.get('items', [])) if 'items' in data else 0
                })
            else:
                print(f"❌ 失败 - 状态码: {response.status_code}")
                print(f"   💬 错误信息: {response.text}")
                results.append({
                    "test": test['name'],
                    "status": "FAILED",
                    "status_code": response.status_code,
                    "error": response.text
                })
                
        except requests.RequestException as e:
            print(f"🌐 网络错误: {str(e)}")
            results.append({
                "test": test['name'],
                "status": "ERROR",
                "error": str(e)
            })
    
    # 打印测试结果摘要
    print("\n" + "="*50)
    print("📊 测试结果摘要")
    print("="*50)
    
    success_count = len([r for r in results if r['status'] == 'SUCCESS'])
    failed_count = len([r for r in results if r['status'] == 'FAILED'])
    error_count = len([r for r in results if r['status'] == 'ERROR'])
    
    print(f"✅ 成功: {success_count}")
    print(f"❌ 失败: {failed_count}")
    print(f"🌐 错误: {error_count}")
    print(f"📊 总计: {len(results)}")
    
    if failed_count > 0 or error_count > 0:
        print("\n❌ 失败的测试:")
        for result in results:
            if result['status'] != 'SUCCESS':
                print(f"   - {result['test']}: {result['status']}")
                if 'error' in result:
                    print(f"     错误: {result['error']}")
    
    return success_count == len(results)

def test_health():
    """测试服务健康状态"""
    try:
        print("🏥 检查服务健康状态...")
        response = requests.get(f"{BASE_URL}/../health", timeout=5)
        if response.status_code == 200:
            print("✅ 服务运行正常")
            return True
        else:
            print(f"❌ 服务状态异常: {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"❌ 无法连接到服务: {str(e)}")
        print("💡 请确保后端服务已启动 (python main.py)")
        return False

if __name__ == "__main__":
    # 首先检查服务健康状态
    if not test_health():
        sys.exit(1)
    
    # 运行API测试
    success = test_api()
    
    if success:
        print("\n🎉 所有测试通过！同城服务API工作正常。")
        sys.exit(0)
    else:
        print("\n💥 部分测试失败！请检查API实现。")
        sys.exit(1)

