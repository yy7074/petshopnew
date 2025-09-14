#!/usr/bin/env python3
import requests
import json
import sys
import os

sys.path.append('/Users/yy/Documents/GitHub/petshopnew/backend')

def test_home_api():
    try:
        response = requests.get('http://localhost:8000/api/home')
        print(f'状态码: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            print('API响应结构:')
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # 检查hot_products
            if 'hot_products' in data:
                hot_products = data['hot_products']
                print(f'\nhot_products数量: {len(hot_products)}')
                if hot_products:
                    first_product = hot_products[0]
                    print(f'第一个商品字段: {list(first_product.keys())}')
                    print(f'seller_id: {first_product.get("seller_id", "字段不存在")}')
        else:
            print(f'API错误: {response.text}')
            
    except requests.exceptions.ConnectionError:
        print('无法连接到后端API，请确保后端服务正在运行')
    except Exception as e:
        print(f'测试出错: {e}')

if __name__ == '__main__':
    test_home_api()
