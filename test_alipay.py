#!/usr/bin/env python3
"""
支付宝支付测试脚本
用于测试支付宝沙箱环境的支付功能
"""

import requests
import json
from datetime import datetime

# API基础URL
BASE_URL = "https://catdog.dachaonet.com/api"

# 测试用户登录信息
TEST_USER = {
    "phone": "13800138000",  # 需要先注册这个测试用户
    "code": "123456"  # 测试验证码
}

def login():
    """用户登录获取token"""
    login_url = f"{BASE_URL}/auth/sms/login"
    response = requests.post(login_url, json=TEST_USER)
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print(f"✅ 登录成功，Token: {token[:20]}...")
        return token
    else:
        print(f"❌ 登录失败: {response.text}")
        return None

def create_test_order(token):
    """创建测试订单"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    order_data = {
        "product_id": 1,  # 需要确保数据库中有这个商品
        "final_price": 0.01,  # 测试金额1分钱
        "shipping_fee": 0.00,
        "total_amount": 0.01,
        "payment_method": 1,  # 支付宝
        "shipping_address": {
            "name": "测试用户",
            "phone": "13800138000",
            "province": "北京市",
            "city": "北京市",
            "district": "朝阳区",
            "address": "测试地址123号",
            "is_default": True
        }
    }
    
    create_url = f"{BASE_URL}/orders/"
    response = requests.post(create_url, json=order_data, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        order_id = data.get("id")
        print(f"✅ 创建订单成功，订单ID: {order_id}")
        return order_id
    else:
        print(f"❌ 创建订单失败: {response.text}")
        return None

def create_alipay_web_payment(token, order_id):
    """创建支付宝网页支付"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payment_data = {
        "return_url": "https://catdog.dachaonet.com/payment/success",
        "notify_url": f"https://catdog.dachaonet.com/api/orders/payments/1/alipay/notify"
    }
    
    payment_url = f"{BASE_URL}/orders/{order_id}/alipay/web"
    response = requests.post(payment_url, json=payment_data, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            payment_url = data.get("payment_url")
            print(f"✅ 创建支付宝支付成功")
            print(f"🔗 支付链接: {payment_url}")
            print(f"💡 请在浏览器中打开上述链接完成支付测试")
            return payment_url
        else:
            print(f"❌ 创建支付失败: {data}")
            return None
    else:
        print(f"❌ 创建支付失败: {response.text}")
        return None

def create_alipay_app_payment(token, order_id):
    """创建支付宝App支付"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payment_url = f"{BASE_URL}/orders/{order_id}/alipay/app"
    response = requests.post(payment_url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            payment_data = data.get("data")
            print(f"✅ 创建支付宝App支付成功")
            print(f"📱 支付参数: {payment_data.get('order_string')}")
            return payment_data
        else:
            print(f"❌ 创建App支付失败: {data}")
            return None
    else:
        print(f"❌ 创建App支付失败: {response.text}")
        return None

def query_payment_status(token, payment_id):
    """查询支付状态"""
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    query_url = f"{BASE_URL}/orders/payments/{payment_id}/alipay/query"
    response = requests.get(query_url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            payment_info = data.get("data")
            print(f"✅ 查询支付状态成功")
            print(f"📊 支付信息: {json.dumps(payment_info, indent=2, ensure_ascii=False)}")
            return payment_info
        else:
            print(f"❌ 查询支付状态失败: {data}")
            return None
    else:
        print(f"❌ 查询支付状态失败: {response.text}")
        return None

def test_payment_flow():
    """完整的支付流程测试"""
    print("🚀 开始支付宝支付流程测试")
    print("=" * 50)
    
    # 1. 用户登录
    print("\n1️⃣ 用户登录...")
    token = login()
    if not token:
        return
    
    # 2. 创建订单
    print("\n2️⃣ 创建测试订单...")
    order_id = create_test_order(token)
    if not order_id:
        return
    
    # 3. 创建支付宝网页支付
    print("\n3️⃣ 创建支付宝网页支付...")
    payment_url = create_alipay_web_payment(token, order_id)
    
    # 4. 创建支付宝App支付
    print("\n4️⃣ 创建支付宝App支付...")
    app_payment = create_alipay_app_payment(token, order_id)
    
    print("\n" + "=" * 50)
    print("✅ 支付宝支付测试完成!")
    print("\n📝 测试说明:")
    print("1. 网页支付: 在浏览器中打开支付链接")
    print("2. App支付: 将order_string参数传给支付宝App SDK")
    print("3. 支付宝沙箱测试账号:")
    print("   - 买家账号: jjskvq3542@sandbox.com")
    print("   - 登录密码: 111111")
    print("   - 支付密码: 111111")

def simulate_payment_notify():
    """模拟支付宝回调通知（用于测试）"""
    print("\n🔔 模拟支付宝回调通知...")
    
    # 模拟支付成功的回调数据
    notify_data = {
        "trade_status": "TRADE_SUCCESS",
        "out_trade_no": "ORDER_1_20241213143000",  # 需要替换为实际的订单号
        "trade_no": "2024121322001443841000001",
        "total_amount": "0.01",
        "app_id": "9021000122686135"
    }
    
    notify_url = f"{BASE_URL}/orders/payments/1/alipay/notify"  # payment_id需要替换
    response = requests.post(notify_url, json=notify_data)
    
    print(f"回调结果: {response.text}")

if __name__ == "__main__":
    print("支付宝支付测试脚本")
    print("请确保:")
    print("1. 后端服务已启动 (python -m uvicorn main:app --reload)")
    print("2. 数据库中存在测试用户和商品数据")
    print("3. 已配置支付宝沙箱密钥")
    print()
    
    choice = input("选择测试类型 (1-完整流程测试, 2-模拟回调通知): ")
    
    if choice == "1":
        test_payment_flow()
    elif choice == "2":
        simulate_payment_notify()
    else:
        print("无效选择")