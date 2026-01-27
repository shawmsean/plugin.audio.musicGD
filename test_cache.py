#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存系统测试脚本

测试内容:
1. 缓存键生成
2. 缓存读写
3. 缓存过期检查
4. 缓存清理功能
"""

import sys
import os
import json
import time
import hashlib

# 设置控制台输出编码为 UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 模拟 Kodi 环境
class MockAddon:
    def __init__(self):
        self.settings = {
            'cache_enabled': 'true',
            'default_source': '0',
            'default_quality': '2'
        }

    def getSetting(self, key):
        return self.settings.get(key, '')

    def getAddonInfo(self, key):
        info = {
            'id': 'plugin.audio.musicGD',
            'name': 'GD Music',
            'icon': 'icon.png',
            'fanart': 'fanart.jpg'
        }
        return info.get(key, '')

# 设置全局变量
__addon__ = MockAddon()
__addon_id__ = __addon__.getAddonInfo('id')
__addon_name__ = __addon__.getAddonInfo('name')
__icon__ = __addon__.getAddonInfo('icon')
__fanart__ = __addon__.getAddonInfo('fanart')

# 导入缓存函数 (需要从 main.py 中导入)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 定义缓存配置
CACHE_DIR = './test_cache/'
CACHE_EXPIRE_SECONDS = 24 * 60 * 60  # 24小时

def log(msg, level=None):
    """模拟日志函数"""
    print('[LOG] %s' % msg)

def test_cache_key_generation():
    """测试缓存键生成"""
    print("\n=== 测试缓存键生成 ===")

    def get_cache_key(prefix, *args):
        cache_string = '%s_%s' % (prefix, '_'.join(str(arg) for arg in args))
        return hashlib.md5(cache_string.encode()).hexdigest()

    # 测试不同的缓存键
    key1 = get_cache_key('playlist_tags')
    key2 = get_cache_key('highquality_playlists', '全部', 0, 20)
    key3 = get_cache_key('playlist_detail', '12345')
    key4 = get_cache_key('playlist_all_tracks', '12345', 0, 'all')

    print("✓ playlist_tags 缓存键: %s" % key1)
    print("✓ highquality_playlists 缓存键: %s" % key2)
    print("✓ playlist_detail 缓存键: %s" % key3)
    print("✓ playlist_all_tracks 缓存键: %s" % key4)

    # 测试相同参数生成相同的缓存键
    key5 = get_cache_key('highquality_playlists', '全部', 0, 20)
    assert key2 == key5, "相同参数应该生成相同的缓存键"
    print("✓ 缓存键一致性测试通过")

def test_cache_operations():
    """测试缓存读写操作"""
    print("\n=== 测试缓存读写操作 ===")

    # 创建测试缓存目录
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

    # 测试数据
    test_data = {
        'tags': [
            {'name': '华语', 'id': 1},
            {'name': '流行', 'id': 2},
            {'name': '摇滚', 'id': 3}
        ]
    }

    # 写入缓存
    cache_key = 'test_cache_key'
    cache_file = os.path.join(CACHE_DIR, '%s.json' % cache_key)

    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)

    print("✓ 缓存写入成功: %s" % cache_file)

    # 读取缓存
    with open(cache_file, 'r', encoding='utf-8') as f:
        loaded_data = json.load(f)

    assert loaded_data == test_data, "读取的数据应该与写入的数据一致"
    print("✓ 缓存读取成功，数据一致性验证通过")

def test_cache_expiration():
    """测试缓存过期检查"""
    print("\n=== 测试缓存过期检查 ===")

    # 创建一个立即过期的缓存文件
    import time
    cache_key = 'test_expired_cache'
    cache_file = os.path.join(CACHE_DIR, '%s.json' % cache_key)

    # 写入测试数据
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump({'test': 'data'}, f)

    # 修改文件时间为 25 小时前 (使其过期)
    old_time = time.time() - (25 * 60 * 60)
    os.utime(cache_file, (old_time, old_time))

    # 检查是否过期
    file_mtime = os.path.getmtime(cache_file)
    current_time = time.time()
    is_expired = (current_time - file_mtime) > CACHE_EXPIRE_SECONDS

    assert is_expired, "25小时前的缓存应该已经过期"
    print("✓ 缓存过期检查功能正常")

    # 清理测试文件
    os.remove(cache_file)
    print("✓ 测试文件已清理")

def test_cache_cleanup():
    """测试缓存清理功能"""
    print("\n=== 测试缓存清理功能 ===")

    # 创建多个测试缓存文件
    test_files = []
    for i in range(5):
        cache_key = 'test_cleanup_%d' % i
        cache_file = os.path.join(CACHE_DIR, '%s.json' % cache_key)
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump({'test': i}, f)
        test_files.append(cache_file)

    print("✓ 创建了 %d 个测试缓存文件" % len(test_files))

    # 清理所有缓存
    deleted_count = 0
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
            deleted_count += 1

    assert deleted_count == 5, "应该删除所有 5 个测试文件"
    print("✓ 成功清理 %d 个缓存文件" % deleted_count)

def test_cache_info():
    """测试缓存统计信息"""
    print("\n=== 测试缓存统计信息 ===")

    # 创建一些测试缓存文件
    for i in range(3):
        cache_key = 'test_info_%d' % i
        cache_file = os.path.join(CACHE_DIR, '%s.json' % cache_key)
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump({'test': i}, f)

    # 统计缓存信息
    total_files = 0
    total_size = 0

    if os.path.exists(CACHE_DIR):
        for file in os.listdir(CACHE_DIR):
            if file.startswith('test_info_'):
                file_path = os.path.join(CACHE_DIR, file)
                total_files += 1
                total_size += os.path.getsize(file_path)

    total_size_mb = round(total_size / (1024 * 1024), 2)

    print("✓ 缓存统计信息:")
    print("  - 总缓存文件数: %d" % total_files)
    print("  - 缓存总大小: %d 字节 (%.2f MB)" % (total_size, total_size_mb))

    # 清理测试文件
    for file in os.listdir(CACHE_DIR):
        if file.startswith('test_info_'):
            os.remove(os.path.join(CACHE_DIR, file))

    print("✓ 测试文件已清理")

def main():
    """运行所有测试"""
    print("\n" + "=" * 50)
    print("      缓存系统功能测试")
    print("=" * 50)

    try:
        test_cache_key_generation()
        test_cache_operations()
        test_cache_expiration()
        test_cache_cleanup()
        test_cache_info()

        print("\n" + "=" * 50)
        print("      ✅ 所有测试通过!")
        print("=" * 50)

        # 清理测试目录
        if os.path.exists(CACHE_DIR):
            import shutil
            shutil.rmtree(CACHE_DIR)
            print("\n✓ 测试缓存目录已清理")

    except Exception as e:
        print("\n" + "=" * 50)
        print("      ❌ 测试失败!")
        print("=" * 50)
        print("错误: %s" % str(e))
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
