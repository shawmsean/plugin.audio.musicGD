#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test script for plugin.audio.musicGD

import sys
import os

# Add plugin directory to path
plugin_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, plugin_dir)

def test_url_encoding():
    """Test URL encoding fix"""
    print("=" * 60)
    print("测试 1: URL 编码修复")
    print("=" * 60)
    
    from main import api_call
    
    # Test with Chinese characters
    query = '周杰伦'
    print(f"测试查询: {query}")
    
    result = api_call('search', source='netease', name=query, count='5', pages='1')
    
    if result is None:
        print("❌ 失败: API 返回 None")
        return False
    
    if isinstance(result, list) and len(result) > 0:
        print(f"✅ 成功: 找到 {len(result)} 条结果")
        print(f"   第一条: {result[0].get('name', '')} - {', '.join(result[0].get('artist', []))}")
        return True
    else:
        print("❌ 失败: 没有找到结果")
        return False

def test_play_url():
    """Test play URL retrieval"""
    print("\n" + "=" * 60)
    print("测试 2: 获取播放 URL")
    print("=" * 60)
    
    from main import api_call
    
    track_id = '5257138'  # 周杰伦 - 屋顶
    print(f"测试曲目 ID: {track_id}")
    
    result = api_call('url', source='netease', id=track_id, br='320')
    
    if result is None:
        print("❌ 失败: API 返回 None")
        return False
    
    if 'url' in result:
        print(f"✅ 成功: 获取到播放 URL")
        print(f"   URL: {result['url'][:60]}...")
        print(f"   音质: {result.get('br', 'N/A')}")
        print(f"   大小: {result.get('size', 'N/A')} KB")
        return True
    else:
        print("❌ 失败: 响应中没有 URL")
        return False

def test_album_art():
    """Test album art retrieval"""
    print("\n" + "=" * 60)
    print("测试 3: 获取专辑封面")
    print("=" * 60)
    
    from main import api_call
    
    pic_id = '109951165671182684'
    print(f"测试图片 ID: {pic_id}")
    
    result = api_call('pic', source='netease', id=pic_id, size='500')
    
    if result is None:
        print("❌ 失败: API 返回 None")
        return False
    
    if 'url' in result:
        print(f"✅ 成功: 获取到图片 URL")
        print(f"   URL: {result['url'][:60]}...")
        return True
    else:
        print("❌ 失败: 响应中没有 URL")
        return False

def test_lyrics():
    """Test lyrics retrieval"""
    print("\n" + "=" * 60)
    print("测试 4: 获取歌词")
    print("=" * 60)
    
    from main import api_call
    
    lyric_id = '5257138'
    print(f"测试歌词 ID: {lyric_id}")
    
    result = api_call('lyric', source='netease', id=lyric_id)
    
    if result is None:
        print("❌ 失败: API 返回 None")
        return False
    
    if 'lyric' in result:
        lyric = result['lyric']
        print(f"✅ 成功: 获取到歌词")
        print(f"   长度: {len(lyric)} 字符")
        print(f"   预览: {lyric[:100]}...")
        return True
    else:
        print("❌ 失败: 响应中没有歌词")
        return False

def test_input_validation():
    """Test input validation"""
    print("\n" + "=" * 60)
    print("测试 5: 输入验证")
    print("=" * 60)
    
    from main import validate_query
    
    test_cases = [
        ('', False, '空字符串'),
        ('   ', False, '仅空格'),
        ('周杰伦', True, '正常中文'),
        ('Jay Chou', True, '英文'),
        ('稻香', True, '中文'),
        ('a', True, '单个字符'),
    ]
    
    all_passed = True
    for query, expected, description in test_cases:
        result = validate_query(query)
        status = '✅' if result == expected else '❌'
        print(f"{status} {description}: '{query}' -> {result}")
        if result != expected:
            all_passed = False
    
    return all_passed

def test_rate_limiting():
    """Test rate limiting"""
    print("\n" + "=" * 60)
    print("测试 6: 速率限制")
    print("=" * 60)
    
    from main import log_request, requests_log
    
    # Clear previous logs
    requests_log.clear()
    
    print("测试前请求次数:", len(requests_log))
    
    # Make 10 requests
    for i in range(10):
        log_request()
    
    print("测试后请求次数:", len(requests_log))
    
    if len(requests_log) == 10:
        print("✅ 成功: 速率限制功能正常")
        return True
    else:
        print("❌ 失败: 速率限制计数错误")
        return False

def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "plugin.audio.musicGD 测试套件" + " " * 15 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    tests = [
        ("URL 编码修复", test_url_encoding),
        ("获取播放 URL", test_play_url),
        ("获取专辑封面", test_album_art),
        ("获取歌词", test_lyrics),
        ("输入验证", test_input_validation),
        ("速率限制", test_rate_limiting),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ 测试 '{name}' 发生异常: {str(e)}")
            results.append((name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} {name}")
    
    print()
    print(f"总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！插件修复成功！")
        return 0
    else:
        print("⚠️  部分测试失败，请检查修复内容")
        return 1

if __name__ == '__main__':
    sys.exit(main())
