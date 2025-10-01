#!/usr/bin/env python3
"""
店铺入驻流程完整性测试脚本

测试流程：
1. 用户登录
2. 提交店铺申请
3. 管理员审核申请
4. 标记支付完成
5. 从申请创建店铺
"""

import requests
import json
import sys

# API配置
BASE_URL = "https://catdog.dachaonet.com/api/v1"
ADMIN_URL = "https://catdog.dachaonet.com/api/v1"

# 测试结果收集
test_results = []

def log_test(test_name, success, message=""):
    """记录测试结果"""
    status = "✅ 通过" if success else "❌ 失败"
    result = f"{status} - {test_name}"
    if message:
        result += f": {message}"
    test_results.append(result)
    print(result)
    return success

def test_user_login():
    """测试用户登录"""
    print("\n=== 测试1: 用户登录 ===")
    
    # 使用测试账号登录
    login_data = {
        "username": "13800138000",
        "password": "test123456"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data=login_data,  # 使用表单数据而不是JSON
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                log_test("用户登录", True, f"获得Token: {data['access_token'][:20]}...")
                return data["access_token"]
            else:
                log_test("用户登录", False, "响应中没有access_token")
                return None
        else:
            log_test("用户登录", False, f"状态码: {response.status_code}, 内容: {response.text}")
            return None
    except Exception as e:
        log_test("用户登录", False, f"异常: {str(e)}")
        return None

def test_admin_login():
    """测试管理员登录"""
    print("\n=== 测试2: 管理员登录 ===")
    
    # 使用管理员账号登录
    login_data = {
        "username": "18888888888",
        "password": "admin123"
    }
    
    try:
        response = requests.post(
            f"{ADMIN_URL}/auth/login",
            data=login_data,  # 使用表单数据而不是JSON
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                log_test("管理员登录", True, f"获得Token: {data['access_token'][:20]}...")
                return data["access_token"]
            else:
                log_test("管理员登录", False, "响应中没有access_token")
                return None
        else:
            log_test("管理员登录", False, f"状态码: {response.status_code}, 内容: {response.text}")
            return None
    except Exception as e:
        log_test("管理员登录", False, f"异常: {str(e)}")
        return None

def test_submit_application(user_token):
    """测试提交店铺申请"""
    print("\n=== 测试3: 提交店铺申请 ===")
    
    application_data = {
        "store_name": "测试宠物店",
        "store_description": "这是一个测试店铺，专门售卖优质宠物用品",
        "store_type": "个人店",
        "consignee_name": "张三",
        "consignee_phone": "13800138000",
        "return_region": "山东省济南市历下区",
        "return_address": "测试街道123号",
        "real_name": "张三",
        "id_number": "370102199001011234",
        "id_start_date": "2020-01-01",
        "id_end_date": "2030-01-01",
        "id_front_image": "/static/uploads/test_id_front.jpg",
        "id_back_image": "/static/uploads/test_id_back.jpg",
        "business_license_image": None
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/store-applications/",
            json=application_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {user_token}"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            log_test("提交店铺申请", True, f"申请ID: {data.get('id')}, 状态: {data.get('status')}")
            return data.get("id")
        else:
            log_test("提交店铺申请", False, f"状态码: {response.status_code}, 内容: {response.text}")
            return None
    except Exception as e:
        log_test("提交店铺申请", False, f"异常: {str(e)}")
        return None

def test_get_my_application(user_token):
    """测试获取我的店铺申请"""
    print("\n=== 测试4: 获取我的店铺申请 ===")
    
    try:
        response = requests.get(
            f"{BASE_URL}/store-applications/my",
            headers={
                "Authorization": f"Bearer {user_token}"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            if data:
                log_test("获取我的店铺申请", True, f"申请ID: {data.get('id')}")
                return True
            else:
                log_test("获取我的店铺申请", False, "没有找到申请记录")
                return False
        else:
            log_test("获取我的店铺申请", False, f"状态码: {response.status_code}")
            return False
    except Exception as e:
        log_test("获取我的店铺申请", False, f"异常: {str(e)}")
        return False

def test_admin_get_applications(admin_token):
    """测试管理员获取申请列表"""
    print("\n=== 测试5: 管理员获取申请列表 ===")
    
    try:
        response = requests.get(
            f"{ADMIN_URL}/store-applications/",
            headers={
                "Authorization": f"Bearer {admin_token}"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])
            log_test("管理员获取申请列表", True, f"共 {len(items)} 个申请")
            return True
        else:
            log_test("管理员获取申请列表", False, f"状态码: {response.status_code}")
            return False
    except Exception as e:
        log_test("管理员获取申请列表", False, f"异常: {str(e)}")
        return False

def test_admin_review_application(admin_token, application_id):
    """测试管理员审核申请"""
    print("\n=== 测试6: 管理员审核申请 ===")
    
    review_data = {
        "status": 1,  # 审核通过
        "reject_reason": None
    }
    
    try:
        response = requests.post(
            f"{ADMIN_URL}/store-applications/{application_id}/review",
            json=review_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {admin_token}"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            log_test("管理员审核申请", True, f"审核结果: 通过")
            return True
        else:
            log_test("管理员审核申请", False, f"状态码: {response.status_code}, 内容: {response.text}")
            return False
    except Exception as e:
        log_test("管理员审核申请", False, f"异常: {str(e)}")
        return False

def test_mark_payment_completed(user_token, application_id):
    """测试标记支付完成"""
    print("\n=== 测试7: 标记支付完成 ===")
    
    try:
        response = requests.post(
            f"{BASE_URL}/store-applications/{application_id}/payment-completed",
            headers={
                "Authorization": f"Bearer {user_token}"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            log_test("标记支付完成", True, f"支付状态: {data.get('payment_status')}")
            return True
        else:
            log_test("标记支付完成", False, f"状态码: {response.status_code}, 内容: {response.text}")
            return False
    except Exception as e:
        log_test("标记支付完成", False, f"异常: {str(e)}")
        return False

def test_create_store_from_application(user_token, application_id):
    """测试从申请创建店铺"""
    print("\n=== 测试8: 从申请创建店铺 ===")
    
    try:
        response = requests.post(
            f"{BASE_URL}/store-applications/{application_id}/create-store",
            headers={
                "Authorization": f"Bearer {user_token}"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            log_test("从申请创建店铺", True, f"店铺ID: {data.get('store_id')}")
            return data.get("store_id")
        else:
            log_test("从申请创建店铺", False, f"状态码: {response.status_code}, 内容: {response.text}")
            return None
    except Exception as e:
        log_test("从申请创建店铺", False, f"异常: {str(e)}")
        return None

def test_check_store_api():
    """测试店铺API端点是否存在"""
    print("\n=== 测试9: 检查店铺API端点 ===")
    
    endpoints = [
        "/store-applications/types",
        "/stores/"
    ]
    
    all_ok = True
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            if response.status_code in [200, 401, 403]:  # 401/403表示端点存在但需要认证
                log_test(f"API端点检查: {endpoint}", True, f"状态码: {response.status_code}")
            else:
                log_test(f"API端点检查: {endpoint}", False, f"状态码: {response.status_code}")
                all_ok = False
        except Exception as e:
            log_test(f"API端点检查: {endpoint}", False, f"异常: {str(e)}")
            all_ok = False
    
    return all_ok

def main():
    """主测试流程"""
    print("\n" + "="*60)
    print("店铺入驻流程完整性测试")
    print("="*60)
    
    # 检查API端点
    test_check_store_api()
    
    # 用户登录
    user_token = test_user_login()
    if not user_token:
        print("\n❌ 用户登录失败，无法继续测试")
        print_summary()
        return
    
    # 管理员登录
    admin_token = test_admin_login()
    if not admin_token:
        print("\n⚠️  管理员登录失败，部分测试将跳过")
    
    # 提交店铺申请或获取现有申请
    application_id = test_submit_application(user_token)
    if not application_id:
        print("\n⚠️  可能已有申请，尝试获取现有申请...")
        # 尝试获取现有申请
        try:
            response = requests.get(
                f"{BASE_URL}/store-applications/my",
                headers={"Authorization": f"Bearer {user_token}"}
            )
            if response.status_code == 200:
                data = response.json()
                if data:
                    application_id = data.get('id')
                    print(f"✅ 找到现有申请: ID={application_id}, 状态={data.get('status')}")
                else:
                    print("\n❌ 没有找到申请，无法继续测试")
                    print_summary()
                    return
            else:
                print("\n❌ 获取申请失败，无法继续测试")
                print_summary()
                return
        except Exception as e:
            print(f"\n❌ 异常: {e}")
            print_summary()
            return
    
    # 获取我的申请
    test_get_my_application(user_token)
    
    # 管理员操作
    if admin_token:
        test_admin_get_applications(admin_token)
        
        # 获取申请状态
        try:
            response = requests.get(
                f"{BASE_URL}/store-applications/my",
                headers={"Authorization": f"Bearer {user_token}"}
            )
            application_status = response.json().get('status') if response.status_code == 200 else 0
            payment_status = response.json().get('payment_status') if response.status_code == 200 else 0
            
            print(f"\n当前申请状态: {application_status} (0=待审核,1=审核通过,2=拒绝,3=已开店)")
            print(f"当前支付状态: {payment_status} (0=未支付,1=已支付)")
            
            # 如果未审核，进行审核
            if application_status == 0:
                if test_admin_review_application(admin_token, application_id):
                    application_status = 1
            
            # 如果已审核通过但未支付，标记支付完成
            if application_status == 1 and payment_status == 0:
                if test_mark_payment_completed(user_token, application_id):
                    payment_status = 1
            
            # 如果已支付且未开店，创建店铺
            if application_status == 1 and payment_status == 1:
                test_create_store_from_application(user_token, application_id)
        except Exception as e:
            print(f"\n⚠️  检查申请状态异常: {e}")
    
    # 打印测试总结
    print_summary()

def print_summary():
    """打印测试总结"""
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    passed = sum(1 for r in test_results if "✅" in r)
    failed = sum(1 for r in test_results if "❌" in r)
    total = len(test_results)
    
    print(f"\n总计: {total} 个测试")
    print(f"通过: {passed} 个")
    print(f"失败: {failed} 个")
    print(f"成功率: {passed/total*100:.1f}%")
    
    if failed > 0:
        print("\n失败的测试:")
        for result in test_results:
            if "❌" in result:
                print(f"  {result}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()

