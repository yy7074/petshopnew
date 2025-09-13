#!/usr/bin/env python3
"""
简单的API测试脚本
测试核心功能的API端点
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_root():
    """测试根路径"""
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ 根路径测试: {response.status_code}")
        print(f"   响应: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ 根路径测试失败: {e}")
        return False

def test_health():
    """测试健康检查"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ 健康检查测试: {response.status_code}")
        print(f"   响应: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ 健康检查测试失败: {e}")
        return False

def test_docs():
    """测试API文档"""
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print(f"✅ API文档测试: {response.status_code}")
        if response.status_code == 200:
            print("   Swagger UI文档可用")
        return True
    except Exception as e:
        print(f"❌ API文档测试失败: {e}")
        return False

def test_categories():
    """测试商品分类API"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/products/categories/")
        print(f"✅ 商品分类API测试: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   返回 {len(data)} 个分类")
        return True
    except Exception as e:
        print(f"❌ 商品分类API测试失败: {e}")
        return False

def test_products():
    """测试商品列表API"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/products/")
        print(f"✅ 商品列表API测试: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   返回 {len(data.get('items', []))} 个商品")
        return True
    except Exception as e:
        print(f"❌ 商品列表API测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试宠物拍卖平台API\n")

    # 等待服务器启动
    print("⏳ 等待服务器启动...")
    time.sleep(3)

    tests = [
        ("根路径", test_root),
        ("健康检查", test_health),
        ("API文档", test_docs),
        ("商品分类", test_categories),
        ("商品列表", test_products),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n📋 测试: {test_name}")
        if test_func():
            passed += 1

    print(f"\n{'='*50}")
    print(f"🎯 测试结果: {passed}/{total} 通过")
    print(f"{'='*50}")

    if passed == total:
        print("🎉 所有测试通过！API服务运行正常")
    else:
        print("⚠️  部分测试失败，请检查服务状态")

if __name__ == "__main__":
    main()