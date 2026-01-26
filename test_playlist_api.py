#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 测试歌单 API

import requests
import json

# API 端点
PLAYLIST_TAGS_URL = 'https://apis.netstart.cn/music/playlist/highquality/tags'
HIGHQUALITY_PLAYLIST_URL = 'https://apis.netstart.cn/music/top/playlist/highquality'
PLAYLIST_DETAIL_URL = 'https://apis.netstart.cn/music/playlist/detail'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
}

def test_playlist_tags():
    """测试获取歌单标签 API"""
    print("=" * 60)
    print("测试 1: 获取歌单标签")
    print("=" * 60)

    try:
        response = requests.get(PLAYLIST_TAGS_URL, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        print(f"状态码: {response.status_code}")
        print(f"数据结构: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}")

        if 'tags' in data:
            tags = data['tags']
            print(f"\n标签数量: {len(tags)}")
            print("\n前 10 个标签:")
            for i, tag in enumerate(tags[:10], 1):
                print(f"{i}. {tag.get('name')} (ID: {tag.get('id')})")

        return data
    except Exception as e:
        print(f"错误: {str(e)}")
        return None

def test_highquality_playlists():
    """测试获取高质量歌单 API"""
    print("\n" + "=" * 60)
    print("测试 2: 获取高质量歌单")
    print("=" * 60)

    try:
        params = {
            'limit': 3
        }
        response = requests.get(HIGHQUALITY_PLAYLIST_URL, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        print(f"状态码: {response.status_code}")
        print(f"数据结构: {json.dumps(data, ensure_ascii=False, indent=2)[:800]}")

        if 'playlists' in data:
            playlists = data['playlists']
            print(f"\n歌单数量: {len(playlists)}")
            print("\n歌单列表:")
            for i, playlist in enumerate(playlists, 1):
                print(f"\n{i}. {playlist.get('name')}")
                print(f"   ID: {playlist.get('id')}")
                print(f"   创建者: {playlist.get('creator', {}).get('nickname')}")
                print(f"   歌曲数: {playlist.get('trackCount')}")
                print(f"   播放量: {playlist.get('playCount')}")
                print(f"   封面: {playlist.get('coverImgUrl')[:50]}...")

        return data
    except Exception as e:
        print(f"错误: {str(e)}")
        return None

def test_playlist_detail():
    """测试获取歌单详情 API"""
    print("\n" + "=" * 60)
    print("测试 3: 获取歌单详情")
    print("=" * 60)

    try:
        params = {
            'id': '24381616'
        }
        response = requests.get(PLAYLIST_DETAIL_URL, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        print(f"状态码: {response.status_code}")
        print(f"数据结构: {json.dumps(data, ensure_ascii=False, indent=2)[:800]}")

        if 'playlist' in data:
            playlist = data['playlist']
            print(f"\n歌单名称: {playlist.get('name')}")
            print(f"歌单 ID: {playlist.get('id')}")
            print(f"创建者: {playlist.get('creator', {}).get('nickname')}")
            print(f"描述: {playlist.get('description')[:100]}...")
            print(f"标签: {[tag for tag in playlist.get('tags', [])]}")
            print(f"歌曲数量: {playlist.get('trackCount')}")

            tracks = playlist.get('tracks', [])
            print(f"\n前 5 首歌曲:")
            for i, track in enumerate(tracks[:5], 1):
                print(f"\n{i}. {track.get('name')}")
                print(f"   ID: {track.get('id')}")
                print(f"   歌手: {', '.join([ar.get('name') for ar in track.get('ar', [])])}")
                print(f"   专辑: {track.get('al', {}).get('name')}")

        return data
    except Exception as e:
        print(f"错误: {str(e)}")
        return None

def main():
    """运行所有测试"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 20 + "歌单 API 测试" + " " * 24 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    # 测试 1: 获取歌单标签
    tags_data = test_playlist_tags()

    # 测试 2: 获取高质量歌单
    playlists_data = test_highquality_playlists()

    # 测试 3: 获取歌单详情
    detail_data = test_playlist_detail()

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    print("\n总结:")
    print(f"[OK] 歌单标签 API: {'成功' if tags_data else '失败'}")
    print(f"[OK] 高质量歌单 API: {'成功' if playlists_data else '失败'}")
    print(f"[OK] 歌单详情 API: {'成功' if detail_data else '失败'}")

if __name__ == '__main__':
    main()
