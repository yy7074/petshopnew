#!/usr/bin/env python3
"""
全面检查所有API功能对接情况
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://39.96.177.57:3000/api/v1"

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def test_api(name, url, method="GET", data=None, headers=None, expect_auth=False):
    """测试API端点"""
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=5)
        
        # 如果期望需要认证，401是正常的
        if expect_auth and response.status_code == 401:
            print(f"  {Colors.GREEN}✓{Colors.END} {name} - 需要认证(正常)")
            return True
        
        # 如果是成功状态码
        if 200 <= response.status_code < 300:
            print(f"  {Colors.GREEN}✓{Colors.END} {name} - 状态码 {response.status_code}")
            return True
        
        # 如果是404，说明端点不存在
        if response.status_code == 404:
            print(f"  {Colors.RED}✗{Colors.END} {name} - {Colors.RED}端点不存在{Colors.END}")
            return False
        
        # 其他状态码
        print(f"  {Colors.YELLOW}⚠{Colors.END} {name} - 状态码 {response.status_code}")
        return None
        
    except requests.exceptions.Timeout:
        print(f"  {Colors.RED}✗{Colors.END} {name} - {Colors.RED}请求超时{Colors.END}")
        return False
    except requests.exceptions.ConnectionError:
        print(f"  {Colors.RED}✗{Colors.END} {name} - {Colors.RED}连接失败{Colors.END}")
        return False
    except Exception as e:
        print(f"  {Colors.RED}✗{Colors.END} {name} - 错误: {e}")
        return False

def main():
    print(f"\n{Colors.BLUE}{'='*80}{Colors.END}")
    print(f"{Colors.BLUE}🔍 开始检查所有API功能对接情况{Colors.END}")
    print(f"{Colors.BLUE}{'='*80}{Colors.END}\n")
    
    results = {
        "success": 0,
        "failed": 0,
        "warning": 0
    }
    
    # 1. 基础服务
    print(f"\n{Colors.BLUE}【1. 基础服务】{Colors.END}")
    r = test_api("健康检查", "http://39.96.177.57:3000/health")
    if r: results["success"] += 1
    elif r is False: results["failed"] += 1
    else: results["warning"] += 1
    
    # 2. 认证相关
    print(f"\n{Colors.BLUE}【2. 认证相关】{Colors.END}")
    apis = [
        ("用户登录", f"{BASE_URL}/auth/login", "POST", {"username": "test", "password": "test"}),
        ("短信登录", f"{BASE_URL}/auth/sms-login", "POST"),
        ("注册", f"{BASE_URL}/auth/register", "POST"),
        ("用户信息", f"{BASE_URL}/auth/profile", "GET", None, None, True),
    ]
    for name, url, *args in apis:
        r = test_api(name, url, *args)
        if r: results["success"] += 1
        elif r is False: results["failed"] += 1
        else: results["warning"] += 1
    
    # 3. 首页相关
    print(f"\n{Colors.BLUE}【3. 首页相关】{Colors.END}")
    apis = [
        ("首页数据", f"{BASE_URL}/home/"),
        ("轮播图", f"{BASE_URL}/home/banners"),
        ("推荐商品", f"{BASE_URL}/home/recommended-products"),
    ]
    for name, url in apis:
        r = test_api(name, url)
        if r: results["success"] += 1
        elif r is False: results["failed"] += 1
        else: results["warning"] += 1
    
    # 4. 商品相关
    print(f"\n{Colors.BLUE}【4. 商品相关】{Colors.END}")
    apis = [
        ("商品列表", f"{BASE_URL}/products/"),
        ("商品分类", f"{BASE_URL}/products/categories"),
        ("商品搜索", f"{BASE_URL}/search?keyword=宠物"),
    ]
    for name, url in apis:
        r = test_api(name, url)
        if r: results["success"] += 1
        elif r is False: results["failed"] += 1
        else: results["warning"] += 1
    
    # 5. 专场活动
    print(f"\n{Colors.BLUE}【5. 专场活动】{Colors.END}")
    apis = [
        ("专场列表", f"{BASE_URL}/events/"),
    ]
    for name, url in apis:
        r = test_api(name, url)
        if r: results["success"] += 1
        elif r is False: results["failed"] += 1
        else: results["warning"] += 1
    
    # 6. 竞拍相关（需要认证）
    print(f"\n{Colors.BLUE}【6. 竞拍相关】{Colors.END}")
    apis = [
        ("竞拍记录", f"{BASE_URL}/bids/", "GET", None, None, True),
        ("拍卖结果", f"{BASE_URL}/auctions/results", "GET", None, None, True),
    ]
    for name, url, *args in apis:
        r = test_api(name, url, *args)
        if r: results["success"] += 1
        elif r is False: results["failed"] += 1
        else: results["warning"] += 1
    
    # 7. 订单相关（需要认证）
    print(f"\n{Colors.BLUE}【7. 订单相关】{Colors.END}")
    apis = [
        ("订单列表", f"{BASE_URL}/orders/", "GET", None, None, True),
    ]
    for name, url, *args in apis:
        r = test_api(name, url, *args)
        if r: results["success"] += 1
        elif r is False: results["failed"] += 1
        else: results["warning"] += 1
    
    # 8. 钱包相关（需要认证）
    print(f"\n{Colors.BLUE}【8. 钱包相关】{Colors.END}")
    apis = [
        ("钱包信息", f"{BASE_URL}/wallet/", "GET", None, None, True),
        ("交易记录", f"{BASE_URL}/wallet/transactions", "GET", None, None, True),
    ]
    for name, url, *args in apis:
        r = test_api(name, url, *args)
        if r: results["success"] += 1
        elif r is False: results["failed"] += 1
        else: results["warning"] += 1
    
    # 9. 保证金相关（需要认证）
    print(f"\n{Colors.BLUE}【9. 保证金相关】{Colors.END}")
    apis = [
        ("保证金列表", f"{BASE_URL}/deposits/", "GET", None, None, True),
    ]
    for name, url, *args in apis:
        r = test_api(name, url, *args)
        if r: results["success"] += 1
        elif r is False: results["failed"] += 1
        else: results["warning"] += 1
    
    # 10. 店铺相关
    print(f"\n{Colors.BLUE}【10. 店铺相关】{Colors.END}")
    apis = [
        ("店铺列表", f"{BASE_URL}/stores/"),
        ("店铺申请", f"{BASE_URL}/store-applications/", "GET", None, None, True),
    ]
    for name, url, *args in apis:
        r = test_api(name, url, *args)
        if r: results["success"] += 1
        elif r is False: results["failed"] += 1
        else: results["warning"] += 1
    
    # 11. 消息聊天（需要认证）
    print(f"\n{Colors.BLUE}【11. 消息聊天】{Colors.END}")
    apis = [
        ("消息列表", f"{BASE_URL}/messages/", "GET", None, None, True),
        ("聊天记录", f"{BASE_URL}/chat/conversations", "GET", None, None, True),
    ]
    for name, url, *args in apis:
        r = test_api(name, url, *args)
        if r: results["success"] += 1
        elif r is False: results["failed"] += 1
        else: results["warning"] += 1
    
    # 12. 同城服务
    print(f"\n{Colors.BLUE}【12. 同城服务】{Colors.END}")
    apis = [
        ("同城服务列表", f"{BASE_URL}/local-services/"),
        ("宠物店列表", f"{BASE_URL}/local-services/stores"),
    ]
    for name, url in apis:
        r = test_api(name, url)
        if r: results["success"] += 1
        elif r is False: results["failed"] += 1
        else: results["warning"] += 1
    
    # 13. 抽奖相关
    print(f"\n{Colors.BLUE}【13. 抽奖相关】{Colors.END}")
    apis = [
        ("抽奖配置", f"{BASE_URL}/lottery/config"),
    ]
    for name, url in apis:
        r = test_api(name, url)
        if r: results["success"] += 1
        elif r is False: results["failed"] += 1
        else: results["warning"] += 1
    
    # 14. 签到相关（需要认证）
    print(f"\n{Colors.BLUE}【14. 签到相关】{Colors.END}")
    apis = [
        ("签到状态", f"{BASE_URL}/checkin/status", "GET", None, None, True),
    ]
    for name, url, *args in apis:
        r = test_api(name, url, *args)
        if r: results["success"] += 1
        elif r is False: results["failed"] += 1
        else: results["warning"] += 1
    
    # 15. 关注粉丝（需要认证）
    print(f"\n{Colors.BLUE}【15. 关注粉丝】{Colors.END}")
    apis = [
        ("关注列表", f"{BASE_URL}/follows/following", "GET", None, None, True),
        ("粉丝列表", f"{BASE_URL}/follows/followers", "GET", None, None, True),
    ]
    for name, url, *args in apis:
        r = test_api(name, url, *args)
        if r: results["success"] += 1
        elif r is False: results["failed"] += 1
        else: results["warning"] += 1
    
    # 16. AI识别
    print(f"\n{Colors.BLUE}【16. AI识别】{Colors.END}")
    apis = [
        ("AI识别端点", f"{BASE_URL}/ai-recognition", "POST", {}, None, False),
    ]
    for name, url, *args in apis:
        r = test_api(name, url, *args)
        if r: results["success"] += 1
        elif r is False: results["failed"] += 1
        else: results["warning"] += 1
    
    # 17. 启动广告
    print(f"\n{Colors.BLUE}【17. 启动广告】{Colors.END}")
    apis = [
        ("启动广告列表", f"{BASE_URL}/splash-ads"),
    ]
    for name, url in apis:
        r = test_api(name, url)
        if r: results["success"] += 1
        elif r is False: results["failed"] += 1
        else: results["warning"] += 1
    
    # 18. 后台管理（需要管理员认证）
    print(f"\n{Colors.BLUE}【18. 后台管理】{Colors.END}")
    apis = [
        ("后台首页", "http://39.96.177.57:3000/admin/"),
        ("管理员API", f"{BASE_URL}/admin/dashboard", "GET", None, None, True),
    ]
    for name, url, *args in apis:
        r = test_api(name, url, *args)
        if r: results["success"] += 1
        elif r is False: results["failed"] += 1
        else: results["warning"] += 1
    
    # 统计结果
    print(f"\n{Colors.BLUE}{'='*80}{Colors.END}")
    print(f"{Colors.BLUE}📊 检查结果统计{Colors.END}")
    print(f"{Colors.BLUE}{'='*80}{Colors.END}")
    print(f"  {Colors.GREEN}✓ 正常: {results['success']}{Colors.END}")
    print(f"  {Colors.RED}✗ 失败: {results['failed']}{Colors.END}")
    print(f"  {Colors.YELLOW}⚠ 警告: {results['warning']}{Colors.END}")
    
    total = results['success'] + results['failed'] + results['warning']
    success_rate = (results['success'] / total * 100) if total > 0 else 0
    
    print(f"\n  成功率: {success_rate:.1f}%")
    
    if results['failed'] > 0:
        print(f"\n{Colors.YELLOW}⚠ 注意：有 {results['failed']} 个API端点不可用，请检查后端实现{Colors.END}")
    else:
        print(f"\n{Colors.GREEN}✓ 所有关键API端点都已就绪！{Colors.END}")
    
    print(f"\n{Colors.BLUE}{'='*80}{Colors.END}\n")

if __name__ == "__main__":
    main()

