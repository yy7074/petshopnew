#!/usr/bin/env python3
import requests
import json
import os

# 清除代理设置
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)

def test_sms_api():
    base_url = "https://catdog.dachaonet.com"
    test_phone = "18663764585"
    
    print("🔍 测试阿里云短信验证码API...")
    print("=" * 50)
    print(f"测试手机号: {test_phone}")
    print()
    
    try:
        # 1. 测试发送短信验证码
        print("1. 测试发送短信验证码...")
        sms_data = {
            "phone": test_phone
        }
        
        response = requests.post(
            f"{base_url}/api/v1/auth/send-sms",
            json=sms_data,
            timeout=10
        )
        
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.json()}")
        print()
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 短信发送成功！")
                if 'code' in result:
                    print(f"   验证码: {result['code']}")
                
                # 2. 测试验证短信验证码
                print("\n2. 测试验证短信验证码...")
                verify_data = {
                    "phone": test_phone,
                    "code": result.get('code', '123456')  # 使用返回的验证码或默认值
                }
                
                verify_response = requests.post(
                    f"{base_url}/api/v1/auth/verify-sms",
                    json=verify_data,
                    timeout=10
                )
                
                print(f"   状态码: {verify_response.status_code}")
                print(f"   响应: {verify_response.json()}")
                print()
                
                # 3. 测试短信登录
                print("3. 测试短信验证码登录...")
                login_data = {
                    "phone": test_phone,
                    "code": result.get('code', '123456')
                }
                
                login_response = requests.post(
                    f"{base_url}/api/v1/auth/sms-login",
                    json=login_data,
                    timeout=10
                )
                
                print(f"   状态码: {login_response.status_code}")
                print(f"   响应: {login_response.json()}")
                print()
                
                if login_response.status_code == 200:
                    print("✅ 短信登录成功！")
                    login_result = login_response.json()
                    if 'access_token' in login_result:
                        print(f"   访问令牌: {login_result['access_token'][:20]}...")
                    if 'user' in login_result:
                        user = login_result['user']
                        print(f"   用户信息: {user.get('nickname', 'N/A')} ({user.get('phone', 'N/A')})")
                else:
                    print("❌ 短信登录失败")
            else:
                print("❌ 短信发送失败")
        else:
            print("❌ 短信发送请求失败")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到API服务")
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_sms_api()
