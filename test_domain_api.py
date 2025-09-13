#!/usr/bin/env python3
import requests
import json
import os

# 清除代理设置
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)

def test_domain_api():
    base_url = "https://catdog.dachaonet.com"
    
    print("🔍 测试域名API接口...")
    print("=" * 50)
    
    try:
        # 测试根路径
        print("1. 测试根路径...")
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.json()}")
        print()
        
        # 测试健康检查
        print("2. 测试健康检查...")
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.json()}")
        print()
        
        # 测试API文档
        print("3. 测试API文档...")
        response = requests.get(f"{base_url}/docs", timeout=10)
        print(f"   状态码: {response.status_code}")
        print(f"   API文档可访问: {response.status_code == 200}")
        print()
        
        # 测试认证接口
        print("4. 测试认证接口...")
        auth_url = f"{base_url}/api/v1/auth"
        response = requests.get(auth_url, timeout=10)
        print(f"   状态码: {response.status_code}")
        print(f"   认证接口可访问: {response.status_code == 200}")
        print()
        
        print("✅ 域名API测试完成！")
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到API服务")
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_domain_api()
