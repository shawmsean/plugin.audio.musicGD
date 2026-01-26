#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 测试 xbmcswift2 路由兼容性

import sys
import os

# Add plugin directory to path
plugin_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, plugin_dir)

def test_parse_xbmcswift2_url():
    """测试 xbmcswift2 URL 解析"""
    print("=" * 60)
    print("测试 1: xbmcswift2 URL 解析")
    print("=" * 60)
    
    from main import parse_xbmcswift2_url
    
    test_cases = [
        ('/current_song_comments/0', {'mode': 'current_song_comments', 'offset': '0'}),
        ('/current_song_comments/50', {'mode': 'current_song_comments', 'offset': '50'}),
        ('/current_song_comments/', {'mode': 'current_song_comments', 'offset': '0'}),
        ('/song_comments/123456/0', {'mode': 'comments', 'id': '123456', 'offset': '0', 'source': 'netease'}),
        ('/song_comments/123456/50', {'mode': 'comments', 'id': '123456', 'offset': '50', 'source': 'netease'}),
        ('/', {}),
        ('', {}),
    ]
    
    all_passed = True
    for url, expected in test_cases:
        result = parse_xbmcswift2_url(url)
        status = '✅' if result == expected else '❌'
        print(f"{status} URL: {url}")
        if result != expected:
            print(f"   期望: {expected}")
            print(f"   实际: {result}")
            all_passed = False
        else:
            print(f"   结果: {result}")
    
    return all_passed

def test_extract_song_id():
    """测试从播放 URL 提取歌曲 ID"""
    print("\n" + "=" * 60)
    print("测试 2: 从播放 URL 提取歌曲 ID")
    print("=" * 60)
    
    from main import extract_song_id_from_play_url
    import unittest.mock as mock
    
    # Mock xbmc.getInfoLabel
    test_cases = [
        {
            'play_url': 'plugin://plugin.audio.musicGD/?mode=play&source=netease&id=5257138&pic_id=123&lyric_id=456',
            'expected_source': 'netease',
            'expected_id': '5257138',
            'description': 'plugin.audio.musicGD URL'
        },
        {
            'play_url': 'plugin://plugin.audio.music/play/song/1811921555/0/0/207/netease/',
            'expected_source': 'netease',
            'expected_id': '1811921555',
            'description': 'plugin.audio.music URL'
        },
        {
            'play_url': '',
            'expected_source': None,
            'expected_id': None,
            'description': '空 URL'
        },
        {
            'play_url': 'http://example.com/song.mp3',
            'expected_source': None,
            'expected_id': None,
            'description': '非插件 URL'
        },
    ]
    
    all_passed = True
    for case in test_cases:
        with mock.patch('main.xbmc.getInfoLabel', return_value=case['play_url']):
            source, track_id = extract_song_id_from_play_url()
            
            expected_source = case['expected_source']
            expected_id = case['expected_id']
            
            status = '✅' if (source == expected_source and track_id == expected_id) else '❌'
            print(f"{status} {case['description']}")
            print(f"   URL: {case['play_url'][:60]}...")
            
            if source != expected_source or track_id != expected_id:
                print(f"   期望: source={expected_source}, id={expected_id}")
                print(f"   实际: source={source}, id={track_id}")
                all_passed = False
            else:
                print(f"   结果: source={source}, id={track_id}")
    
    return all_passed

def test_integration():
    """集成测试"""
    print("\n" + "=" * 60)
    print("测试 3: 集成测试")
    print("=" * 60)
    
    from main import parse_xbmcswift2_url, extract_song_id_from_play_url
    import unittest.mock as mock
    
    # 模拟皮肤调用场景
    print("\n场景: 皮肤调用 /current_song_comments/0")
    
    # 1. 解析 URL
    xbmcswift2_params = parse_xbmcswift2_url('/current_song_comments/0')
    print(f"✅ 解析结果: {xbmcswift2_params}")
    
    # 2. 模拟正在播放 plugin.audio.musicGD 的歌曲
    play_url = 'plugin://plugin.audio.musicGD/?mode=play&source=netease&id=5257138&pic_id=109951165671182684&lyric_id=5257138&name=屋顶&artist=周杰伦&album=Jay'
    
    with mock.patch('main.xbmc.getInfoLabel', return_value=play_url):
        source, track_id = extract_song_id_from_play_url()
        print(f"✅ 提取结果: source={source}, track_id={track_id}")
        
        if source == 'netease' and track_id == '5257138':
            print("✅ 集成测试通过！")
            return True
        else:
            print("❌ 集成测试失败")
            return False

def main():
    """运行所有测试"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "xbmcswift2 兼容性测试" + " " * 17 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    tests = [
        ("xbmcswift2 URL 解析", test_parse_xbmcswift2_url),
        ("从播放 URL 提取歌曲 ID", test_extract_song_id),
        ("集成测试", test_integration),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ 测试 '{name}' 发生异常: {str(e)}")
            import traceback
            traceback.print_exc()
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
        print("🎉 所有测试通过！xbmcswift2 兼容性实现成功！")
        print()
        print("现在你可以:")
        print("1. 使用 plugin.audio.musicGD 播放音乐")
        print("2. 在 Arctic Fuse 3 皮肤的 MUSIC OSD 中点击评论按钮")
        print("3. 插件会自动识别并显示当前播放歌曲的评论")
        return 0
    else:
        print("⚠️  部分测试失败，请检查实现")
        return 1

if __name__ == '__main__':
    sys.exit(main())
