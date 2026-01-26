#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 独立的 xbmcswift2 路由解析测试（不需要 Kodi 环境）

def parse_xbmcswift2_url(path):
    """
    解析 xbmcswift2 风格的 URL 路径
    
    Args:
        path: URL 路径部分 (例如: /current_song_comments/0)
    
    Returns:
        dict: 解析后的参数
    """
    result = {}
    
    # 移除开头的斜杠
    if path.startswith('/'):
        path = path[1:]
    
    # 移除结尾的斜杠
    if path.endswith('/'):
        path = path[:-1]
    
    # 分割路径部分
    parts = path.split('/')
    
    if len(parts) == 0:
        return result
    
    # 识别路由模式
    if parts[0] == 'current_song_comments':
        # /current_song_comments/<offset>
        result['mode'] = 'current_song_comments'
        if len(parts) > 1:
            result['offset'] = parts[1]
        else:
            result['offset'] = '0'
    
    elif parts[0] == 'song_comments':
        # /song_comments/<song_id>/<offset>
        result['mode'] = 'comments'
        if len(parts) > 1:
            result['id'] = parts[1]
        else:
            result['id'] = ''
        if len(parts) > 2:
            result['offset'] = parts[2]
        else:
            result['offset'] = '0'
        # 默认使用 netease 音乐源
        result['source'] = 'netease'
    
    return result


def test_parse_xbmcswift2_url():
    """测试 xbmcswift2 URL 解析"""
    print("=" * 60)
    print("测试: xbmcswift2 URL 解析")
    print("=" * 60)
    
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
        status = 'PASS' if result == expected else 'FAIL'
        print(f"[{status}] URL: {url}")
        if result != expected:
            print(f"   Expected: {expected}")
            print(f"   Got: {result}")
            all_passed = False
        else:
            print(f"   Result: {result}")
    
    return all_passed


if __name__ == '__main__':
    print("\n")
    print("xbmcswift2 Routing Compatibility Test")
    print("=" * 60)
    print()
    
    result = test_parse_xbmcswift2_url()
    
    print()
    print("=" * 60)
    if result:
        print("All tests PASSED!")
        print()
        print("The plugin.audio.musicGD now supports xbmcswift2 routes:")
        print("  - /current_song_comments/<offset>")
        print("  - /song_comments/<song_id>/<offset>")
        print()
        print("This allows Arctic Fuse 3 skin to trigger comments")
        print("for songs played by plugin.audio.musicGD")
    else:
        print("Some tests FAILED!")
    print("=" * 60)
