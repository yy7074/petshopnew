#!/usr/bin/env python3
import requests
import json
import time

def test_api():
    base_url = "http://localhost:8000"
    
    print("🔍 测试宠物拍卖API接口...")
    print("=" * 50)
    
    # 等待服务启动
    print("⏳ 等待服务启动...")
    time.sleep(3)
    
    try:
        # 测试根路径
        print("1. 测试根路径...")
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.json()}")
        print()
        
        # 测试健康检查
        print("2. 测试健康检查...")
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.json()}")
        print()
        
        # 测试API文档
        print("3. 测试API文档...")
        response = requests.get(f"{base_url}/docs", timeout=5)
        print(f"   状态码: {response.status_code}")
        print(f"   API文档可访问: {response.status_code == 200}")
        print()
        
        # 测试认证接口
        print("4. 测试认证接口...")
        auth_url = f"{base_url}/api/v1/auth"
        response = requests.get(auth_url, timeout=5)
        print(f"   状态码: {response.status_code}")
        print(f"   认证接口可访问: {response.status_code == 200}")
        print()
        
        print("✅ API测试完成！")
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到API服务，请确保后台服务正在运行")
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_api()
