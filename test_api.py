#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify API response format
"""

import requests

def test_api_response():
    """Test API response and check format"""
    
    url = "https://music-api.gdstudio.xyz/api.php"
    params = {
        'types': 'search',
        'source': 'netease',
        'name': '晴天',
        'count': '5',
        'pages': '1'
    }
    
    # Test with different headers
    test_cases = [
        ("Original headers", {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
        }),
        ("Fixed headers", {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }),
        ("Minimal headers", {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }),
    ]
    
    for name, headers in test_cases:
        print("\n" + "=" * 60)
        print(f"测试: {name}")
        print("=" * 60)
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            print(f"状态码: {response.status_code}")
            print(f"Content-Type: {response.headers.get('Content-Type', 'unknown')}")
            print(f"Content-Length: {len(response.content)} bytes")
            print(f"Content-Encoding: {response.headers.get('Content-Encoding', 'none')}")
            
            # Show first 200 characters
            preview = response.text[:200] if response.text else ''
            print(f"响应预览: {preview}")
            
            # Try to parse JSON
            try:
                data = response.json()
                print(f"✅ JSON 解析成功")
                
                if isinstance(data, list):
                    print(f"   返回 {len(data)} 条结果")
                    if len(data) > 0:
                        print(f"   第一条: {data[0].get('name', '')}")
                else:
                    print(f"   返回类型: {type(data)}")
                    
            except ValueError as e:
                print(f"❌ JSON 解析失败: {e}")
                print(f"   完整响应: {response.text[:500]}")
                
        except Exception as e:
            print(f"❌ 请求失败: {e}")

if __name__ == '__main__':
    test_api_response()
