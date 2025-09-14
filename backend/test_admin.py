#!/usr/bin/env python3
"""
测试管理员登录功能
"""
import requests
import json

def test_admin_login():
    """测试管理员登录"""
    url = "http://localhost:3000/api/v1/admin/login"
    payload = {
        "username": "admin",
        "password": "admin123456"
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print(f"Login successful! Token: {token[:50]}...")
            return token
        else:
            print("Login failed!")
            return None
            
    except Exception as e:
        print(f"Request failed: {e}")
        return None

def test_admin_verify(token):
    """测试token验证"""
    if not token:
        return
        
    url = "http://localhost:3000/api/v1/admin/verify"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Verify Status Code: {response.status_code}")
        print(f"Verify Response: {response.text}")
        
    except Exception as e:
        print(f"Verify request failed: {e}")

def test_dashboard_stats(token):
    """测试仪表盘统计"""
    if not token:
        return
        
    url = "http://localhost:3000/api/v1/admin/dashboard/stats"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Dashboard Status Code: {response.status_code}")
        print(f"Dashboard Response: {response.text}")
        
    except Exception as e:
        print(f"Dashboard request failed: {e}")

if __name__ == "__main__":
    print("Testing Admin Login API...")
    token = test_admin_login()
    
    if token:
        print("\nTesting Token Verification...")
        test_admin_verify(token)
        
        print("\nTesting Dashboard Stats...")
        test_dashboard_stats(token)