#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Kodi plugin for GD Music API
# Source: GD音乐台(music.gdstudio.xyz)

import sys
import os
import json
import time
import hashlib
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs
import requests
import ssl
from urllib.parse import parse_qs, urlencode

__addon__ = xbmcaddon.Addon()
__addon_id__ = __addon__.getAddonInfo('id')
__addon_name__ = __addon__.getAddonInfo('name')
__icon__ = __addon__.getAddonInfo('icon')
__fanart__ = __addon__.getAddonInfo('fanart')

# Music source mapping (index -> source name)
MUSIC_SOURCES = [
    'netease',
    'kuwo',
    'joox',
    'tencent',
    'tidal',
    'spotify',
    'ytmusic',
    'qobuz',
    'deezer',
    'migu',
    'kugou',
    'ximalaya',
    'apple'
]

# Quality mapping (index -> quality value)
QUALITIES = [
    '128',
    '192',
    '320',
    '740',
    '999'
]

def get_default_source():
    """Get default music source from settings"""
    index = int(__addon__.getSetting('default_source') or '0')
    if 0 <= index < len(MUSIC_SOURCES):
        return MUSIC_SOURCES[index]
    return 'netease'

def get_default_quality():
    """Get default quality from settings"""
    index = int(__addon__.getSetting('default_quality') or '2')
    if 0 <= index < len(QUALITIES):
        return QUALITIES[index]
    return '320'

def get_play_url_with_fallback(track_id, quality='320', song_name='', artist_name=''):
    """
    获取播放 URL，支持多音乐源优先级回退

    优先级顺序：默认音乐源 > kuwo > joox > netease

    Args:
        track_id: 歌曲 ID
        quality: 音质（默认 320）
        song_name: 歌曲名称（用于日志）
        artist_name: 歌手名称（用于日志）

    Returns:
        tuple: (play_url, source) 或 (None, None) 如果所有源都失败
    """
    # 获取用户设置的默认音乐源
    default_source = get_default_source()

    # 定义后备音乐源优先级（排除默认音乐源，避免重复）
    fallback_sources = ['kuwo', 'joox', 'netease']

    # 构建完整的优先级列表：默认音乐源 + 后备音乐源
    source_priority = [default_source] + [s for s in fallback_sources if s != default_source]

    log('Getting play URL with fallback: track_id=%s, quality=%s, song=%s, artist=%s' %
        (track_id, quality, song_name, artist_name))
    log('Source priority: %s' % ' > '.join(source_priority))

    # 按优先级尝试每个音乐源
    for source in source_priority:
        log('Trying source: %s' % source)

        # 尝试获取播放 URL
        data = api_call('url', source=source, id=track_id, br=quality)

        if data and 'url' in data and data['url']:
            play_url = data['url']
            log('Successfully got play URL from %s: %s' % (source, play_url[:80] + '...'))
            return play_url, source

        log('Failed to get play URL from %s' % source)

    # 所有音乐源都失败
    log('All sources failed for track_id=%s' % track_id, xbmc.LOGERROR)
    return None, None

# GD Music API Base URL
BASE_URL = 'https://music-api.gdstudio.xyz/api.php'
CACHE_DIR = xbmcvfs.translatePath('special://profile/addon_data/%s/cache/' % __addon_id__)


def get_cache_expire_seconds():
    """
    从设置中获取缓存过期时间（秒）

    Returns:
        int: 缓存过期时间（秒）
    """
    # 获取设置中的缓存过期时间选项
    cache_expire_option = __addon__.getSetting('cache_expire_time')

    # 根据选项返回对应的秒数
    # 选项值: "0"=1小时, "1"=6小时, "2"=12小时, "3"=24小时, "4"=3天, "5"=7天
    expire_time_map = {
        '0': 1 * 60 * 60,      # 1 小时
        '1': 6 * 60 * 60,      # 6 小时
        '2': 12 * 60 * 60,     # 12 小时
        '3': 24 * 60 * 60,     # 24 小时
        '4': 3 * 24 * 60 * 60, # 3 天
        '5': 7 * 24 * 60 * 60  # 7 天
    }

    # 默认返回 24 小时
    return expire_time_map.get(cache_expire_option, 24 * 60 * 60)


def get_auto_clear_cache():
    """
    从设置中获取是否自动清理过期缓存

    Returns:
        bool: 是否自动清理过期缓存
    """
    return __addon__.getSetting('auto_clear_cache') == 'true'

# Rate limiting: 50 requests per 5 minutes
RATE_LIMIT = 50
RATE_WINDOW = 300  # 5 minutes in seconds
requests_log = []

def log(msg, level=xbmc.LOGINFO):
    """Enhanced logging function"""
    xbmc.log('[%s] %s' % (__addon_id__, msg), level)

def log_request():
    """Log and rate limit API requests"""
    global requests_log
    now = time.time()
    # Clean old requests outside the rate window
    requests_log = [t for t in requests_log if now - t < RATE_WINDOW]
    
    if len(requests_log) >= RATE_LIMIT:
        wait_time = RATE_WINDOW - (now - requests_log[0])
        if wait_time > 0:
            log('Rate limit exceeded. Waiting %d seconds' % int(wait_time), xbmc.LOGWARNING)
            time.sleep(wait_time)
    
    requests_log.append(now)
    log('Request logged. Total requests in window: %d/%d' % (len(requests_log), RATE_LIMIT))

class SSLAdapter(requests.adapters.HTTPAdapter):
    """Custom HTTPAdapter with SSL context"""
    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, *args, **kwargs):
        if self.ssl_context:
            kwargs['ssl_context'] = self.ssl_context
        return super().init_poolmanager(*args, **kwargs)

def create_ssl_context():
    """Create a custom SSL context that mimics browser behavior"""
    context = ssl.create_default_context()
    # Force TLS 1.2 or higher
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.maximum_version = ssl.TLSVersion.TLSv1_3
    # Enable some cipher suites that might be disabled
    context.set_ciphers('HIGH:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!SRP:!CAMELLIA')
    return context

def api_call(types, **params):
    """
    Make API call to GD Music API with retry mechanism
    
    Args:
        types: API type (search, url, pic, lyric)
        **params: Additional parameters for the API
        
    Returns:
        dict: API response data, or None if failed
    """
    log_request()
    
    # Build API URL with parameters
    params['types'] = types
    url = BASE_URL + '?' + urlencode(params)
    
    log('API Request: %s' % url)

    # Browser-like headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'DNT': '1',
        'Connection': 'keep-alive',
    }

    # Retry mechanism: up to 3 attempts with different strategies
    for attempt in range(3):
        try:
            if attempt > 0:
                wait_time = min(2 ** attempt, 10)  # Max 10 seconds
                log('API retry %d/%d in %d seconds' % (attempt + 1, 3, wait_time), xbmc.LOGINFO)
                time.sleep(wait_time)

            https_url = url.replace('http://', 'https://')

            # Try different SSL strategies based on attempt
            if attempt == 0:
                # First attempt: custom SSL context
                ssl_context = create_ssl_context()
                session = requests.Session()
                session.mount('https://', SSLAdapter(ssl_context=ssl_context))
                response = session.get(https_url, headers=headers, timeout=20)
            elif attempt == 1:
                # Second attempt: verify=False (skip SSL verification)
                response = requests.get(https_url, headers=headers, timeout=20, verify=False)
            else:
                # Last attempt: HTTP instead of HTTPS
                http_url = url.replace('https://', 'http://')
                response = requests.get(http_url, headers=headers, timeout=20)

            response.raise_for_status()
            
            # Log response details for debugging
            log('Response status: %d' % response.status_code)
            log('Response content type: %s' % response.headers.get('Content-Type', 'unknown'))
            log('Response content length: %d bytes' % len(response.content))
            
            # Check if response is empty
            if not response.content:
                log('API returned empty response', xbmc.LOGERROR)
                continue
            
            # Log first 200 characters of response for debugging
            response_preview = response.text[:200] if response.text else ''
            log('Response preview: %s' % response_preview)
            
            # Try to parse JSON
            try:
                data = response.json()
            except ValueError as json_error:
                log('JSON parsing failed: %s' % str(json_error), xbmc.LOGERROR)
                log('Full response text: %s' % response.text[:500], xbmc.LOGERROR)
                continue
            
            log('API success on attempt %d' % (attempt + 1))
            if isinstance(data, list):
                log('API returned %d items' % len(data))
            return data

        except requests.exceptions.RequestException as e:
            log('API error on attempt %d/%d: %s' % (attempt + 1, 3, str(e)), xbmc.LOGERROR)
            if attempt == 2:  # Last attempt
                log('All retry attempts failed', xbmc.LOGERROR)
                return None
            continue

    return None

def get_url(**kwargs):
    """Build plugin URL"""
    return '%s?%s' % (sys.argv[0], urlencode(kwargs))

# ==================== 歌单相关 API 函数 ====================

def get_playlist_tags(use_cache=True):
    """
    获取歌单标签列表

    Args:
        use_cache: 是否使用缓存 (默认 True)

    Returns:
        dict: 标签数据，包含 tags 列表，或 None 如果失败
    """
    log('Getting playlist tags')

    # 生成缓存键
    cache_key = get_cache_key('playlist_tags')

    # 尝试从缓存读取
    if use_cache:
        cached_data = get_cached_data(cache_key)
        if cached_data is not None:
            log('Using cached playlist tags')
            return cached_data

    # 从 API 获取数据
    try:
        url = 'https://apis.netstart.cn/music/playlist/highquality/tags'

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()

        if 'tags' in data:
            log('Playlist tags API success: %d tags' % len(data['tags']))

            # 写入缓存
            if use_cache:
                set_cached_data(cache_key, data)

            return data
        else:
            log('Playlist tags API returned no tags', xbmc.LOGERROR)
            return None

    except requests.RequestException as e:
        log('Error getting playlist tags: %s' % str(e), xbmc.LOGERROR)
        return None
    except Exception as e:
        log('Unexpected error getting playlist tags: %s' % str(e), xbmc.LOGERROR)
        return None


def get_highquality_playlists(cat='全部', limit=20, offset=0, use_cache=True):
    """
    获取高质量歌单列表

    Args:
        cat: 歌单分类标签（如：'全部'、'华语'、'流行'等）
        limit: 每页数量
        offset: 偏移量
        use_cache: 是否使用缓存 (默认 True)

    Returns:
        dict: 歌单数据，包含 playlists 列表，或 None 如果失败
    """
    log('Getting highquality playlists: cat=%s, limit=%d, offset=%d' % (cat, limit, offset))

    # 生成缓存键 (包含分类、偏移量、每页数量)
    cache_key = get_cache_key('highquality_playlists', cat, offset, limit)

    # 尝试从缓存读取
    if use_cache:
        cached_data = get_cached_data(cache_key)
        if cached_data is not None:
            log('Using cached highquality playlists: cat=%s, offset=%d' % (cat, offset))
            return cached_data

    # 从 API 获取数据
    try:
        url = 'https://apis.netstart.cn/music/top/playlist/highquality'
        params = {
            'cat': cat,
            'limit': limit,
            'offset': offset
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }

        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()

        if 'playlists' in data:
            log('Highquality playlists API success: %d playlists' % len(data['playlists']))

            # 写入缓存
            if use_cache:
                set_cached_data(cache_key, data)

            return data
        else:
            log('Highquality playlists API returned no playlists', xbmc.LOGERROR)
            return None

    except requests.RequestException as e:
        log('Error getting highquality playlists: %s' % str(e), xbmc.LOGERROR)
        return None
    except Exception as e:
        log('Unexpected error getting highquality playlists: %s' % str(e), xbmc.LOGERROR)
        return None


def get_playlist_detail(playlist_id, use_cache=True):
    """
    获取歌单详情

    Args:
        playlist_id: 歌单 ID
        use_cache: 是否使用缓存 (默认 True)

    Returns:
        dict: 歌单详情数据，包含 playlist 信息和 tracks 列表，或 None 如果失败
    """
    log('Getting playlist detail: id=%s' % playlist_id)

    # 生成缓存键
    cache_key = get_cache_key('playlist_detail', playlist_id)

    # 尝试从缓存读取
    if use_cache:
        cached_data = get_cached_data(cache_key)
        if cached_data is not None:
            log('Using cached playlist detail: id=%s' % playlist_id)
            return cached_data

    # 从 API 获取数据
    try:
        url = 'https://apis.netstart.cn/music/playlist/detail'
        params = {
            'id': playlist_id
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }

        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()

        if 'playlist' in data:
            playlist = data['playlist']
            track_count = len(playlist.get('tracks', []))
            log('Playlist detail API success: %s, %d tracks' % (playlist.get('name'), track_count))

            # 写入缓存
            if use_cache:
                set_cached_data(cache_key, data)

            return data
        else:
            log('Playlist detail API returned no playlist', xbmc.LOGERROR)
            return None

    except requests.RequestException as e:
        log('Error getting playlist detail: %s' % str(e), xbmc.LOGERROR)
        return None
    except Exception as e:
        log('Unexpected error getting playlist detail: %s' % str(e), xbmc.LOGERROR)
        return None


def get_playlist_all_tracks(playlist_id, limit=None, offset=0, use_cache=True):
    """
    获取歌单的所有歌曲

    由于网易云接口限制，歌单详情只会提供 10 首歌，
    通过调用此接口，传入对应的歌单 id，即可获得对应的所有歌曲

    Args:
        playlist_id: 歌单 ID
        limit: 限制获取歌曲的数量，默认值为当前歌单的歌曲数量
        offset: 偏移量，默认值为 0
        use_cache: 是否使用缓存 (默认 True)

    Returns:
        dict: 包含 songs 列表的数据，或 None 如果失败
    """
    log('Getting playlist all tracks: id=%s, limit=%s, offset=%d' % (playlist_id, limit, offset))

    # 生成缓存键 (包含歌单ID、偏移量、限制数量)
    cache_key = get_cache_key('playlist_all_tracks', playlist_id, offset, limit if limit is not None else 'all')

    # 尝试从缓存读取
    if use_cache:
        cached_data = get_cached_data(cache_key)
        if cached_data is not None:
            log('Using cached playlist all tracks: id=%s' % playlist_id)
            return cached_data

    # 从 API 获取数据
    try:
        url = 'https://apis.netstart.cn/music/playlist/track/all'
        params = {
            'id': playlist_id,
            'offset': offset
        }

        # 如果指定了 limit，则添加到参数中
        if limit is not None:
            params['limit'] = limit

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }

        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()

        if 'songs' in data:
            songs = data['songs']
            log('Playlist all tracks API success: %d songs' % len(songs))

            # 写入缓存
            if use_cache:
                set_cached_data(cache_key, data)

            return data
        else:
            log('Playlist all tracks API returned no songs', xbmc.LOGERROR)
            return None

    except requests.RequestException as e:
        log('Error getting playlist all tracks: %s' % str(e), xbmc.LOGERROR)
        return None
    except Exception as e:
        log('Unexpected error getting playlist all tracks: %s' % str(e), xbmc.LOGERROR)
        return None

# ==================== 歌单相关页面函数 ====================

def show_playlist_tags():
    """显示歌单标签列表（文件夹形式）"""
    log('Showing playlist tags')

    # 获取标签列表
    tags_data = get_playlist_tags()

    if not tags_data:
        dialog = xbmcgui.Dialog()
        dialog.notification('错误', '获取歌单标签失败', xbmcgui.NOTIFICATION_ERROR, 2000, False)
        log('Failed to get playlist tags', xbmc.LOGERROR)
        return

    tags = tags_data.get('tags', [])

    # 添加"全部"选项
    add_directory_item('全部', get_url(mode='highquality_playlists', cat='全部'), icon=__icon__, fanart=__fanart__)

    # 添加各个标签
    for tag in tags:
        tag_name = tag.get('name', '')
        tag_id = tag.get('id')

        # 构建标签 URL
        url = get_url(mode='highquality_playlists', cat=tag_name)

        # 添加到列表
        add_directory_item(tag_name, url, is_folder=True, icon=__icon__, fanart=__fanart__)


def show_highquality_playlists(cat='全部', offset=0, limit=20):
    """
    显示高质量歌单列表

    Args:
        cat: 歌单分类标签
        offset: 偏移量
        limit: 每页数量
    """
    log('Showing highquality playlists: cat=%s, offset=%d' % (cat, offset))

    # 获取歌单列表
    playlists_data = get_highquality_playlists(cat=cat, limit=limit, offset=offset)

    if not playlists_data:
        dialog = xbmcgui.Dialog()
        dialog.notification('错误', '获取歌单列表失败', xbmcgui.NOTIFICATION_ERROR, 2000, False)
        log('Failed to get highquality playlists', xbmc.LOGERROR)
        return

    playlists = playlists_data.get('playlists', [])

    if not playlists:
        dialog = xbmcgui.Dialog()
        dialog.notification('提示', '该分类下暂无歌单', xbmcgui.NOTIFICATION_INFO, 2000, False)
        log('No playlists found for category: %s' % cat)
        return

    # 显示歌单列表
    for playlist in playlists:
        name = playlist.get('name', '')
        playlist_id = playlist.get('id')
        creator = playlist.get('creator', {}).get('nickname', '')
        track_count = playlist.get('trackCount', 0)
        play_count = playlist.get('playCount', 0)
        cover_url = playlist.get('coverImgUrl', '')
        description = playlist.get('description', '')

        # 构建标题
        title = name
        if creator:
            title += f' - {creator}'

        # 构建描述
        plot = f'创建者: {creator}\n'
        plot += f'歌曲数: {track_count}\n'
        plot += f'播放量: {play_count}\n'
        if description:
            plot += f'\n{description[:200]}...'

        # 构建信息
        info = {
            'title': name,
            'artist': creator,
            'album': f'{track_count} 首歌曲',
            'plot': plot,
        }

        # 构建歌单 URL
        url = get_url(mode='playlist_detail', id=playlist_id, cat=cat, offset=offset)

        # 添加到列表
        add_directory_item(title, url, is_folder=True, icon=cover_url, fanart=cover_url, info=info)

    # 添加分页按钮
    if len(playlists) == limit:
        # 还有更多歌单，添加"下一页"按钮
        next_url = get_url(mode='highquality_playlists', cat=cat, offset=offset + limit)
        add_directory_item('下一页 >>', next_url, is_folder=True, icon=__icon__, fanart=__fanart__)

    # 添加"返回分类"按钮
    tags_url = get_url(mode='playlist_tags')
    add_directory_item('<< 返回分类', tags_url, is_folder=True, icon=__icon__, fanart=__fanart__)


def show_playlist_detail(playlist_id, cat='全部', offset=0):
    """
    显示歌单详情（歌曲列表）

    Args:
        playlist_id: 歌单 ID
        cat: 歌单分类（用于返回）
        offset: 偏移量（用于返回）
    """
    log('Showing playlist detail: id=%s' % playlist_id)

    # 获取歌单详情（用于获取歌单信息）
    detail_data = get_playlist_detail(playlist_id)

    if not detail_data:
        dialog = xbmcgui.Dialog()
        dialog.notification('错误', '获取歌单详情失败', xbmcgui.NOTIFICATION_ERROR, 2000, False)
        log('Failed to get playlist detail', xbmc.LOGERROR)
        return

    playlist = detail_data.get('playlist', {})

    # 获取歌单的所有歌曲
    all_tracks_data = get_playlist_all_tracks(playlist_id)

    if not all_tracks_data:
        dialog = xbmcgui.Dialog()
        dialog.notification('错误', '获取歌单歌曲失败', xbmcgui.NOTIFICATION_ERROR, 2000, False)
        log('Failed to get playlist all tracks', xbmc.LOGERROR)
        return

    tracks = all_tracks_data.get('songs', [])

    if not tracks:
        dialog = xbmcgui.Dialog()
        dialog.notification('提示', '该歌单暂无歌曲', xbmcgui.NOTIFICATION_INFO, 2000, False)
        log('No tracks found in playlist: %s' % playlist_id)
        return

    # 显示歌单信息
    playlist_name = playlist.get('name', '')
    creator = playlist.get('creator', {}).get('nickname', '')
    description = playlist.get('description', '')

    log('Playlist: %s, %d tracks (all loaded)' % (playlist_name, len(tracks)))

    # 显示歌曲列表
    for track in tracks:
        track_id = track.get('id')
        name = track.get('name', '')
        artists = track.get('ar', [])
        album = track.get('al', {})

        # 提取歌手信息
        artist_names = ', '.join([ar.get('name', '') for ar in artists])
        artist_ids = [ar.get('id') for ar in artists]

        # 提取专辑信息
        album_name = album.get('name', '')
        album_id = album.get('id', 0)
        pic_id = album.get('picId', 0) or album.get('pic', 0)

        # 构建标题
        title = f'{artist_names} - {name}' if artist_names else name

        # 构建信息
        info = {
            'title': name,
            'artist': artist_names,
            'album': album_name,
        }

        # 构建播放 URL（使用 GD Music API）
        url = get_url(
            mode='play',
            source='netease',
            id=track_id,
            pic_id=pic_id,
            name=name,
            artist=artist_names,
            album=album_name
        )

        # 添加到列表
        add_directory_item(title, url, is_folder=False, icon=album.get('picUrl'), fanart=album.get('picUrl'), info=info)

    # 添加"返回歌单列表"按钮
    playlists_url = get_url(mode='highquality_playlists', cat=cat, offset=offset)
    add_directory_item('<< 返回歌单列表', playlists_url, is_folder=True, icon=__icon__, fanart=__fanart__)

    # 添加"播放全部"按钮
    play_all_url = get_url(mode='play_playlist_all', id=playlist_id, cat=cat, offset=offset)
    add_directory_item('▶ 播放全部', play_all_url, is_folder=False, icon=__icon__, fanart=__fanart__)


def play_playlist_all(playlist_id, cat='全部', offset=0):
    """
    播放歌单中的所有歌曲

    Args:
        playlist_id: 歌单 ID
        cat: 歌单分类（用于返回）
        offset: 偏移量（用于返回）
    """
    log('Playing playlist all: id=%s' % playlist_id)

    # 获取歌单的所有歌曲
    all_tracks_data = get_playlist_all_tracks(playlist_id)

    if not all_tracks_data:
        dialog = xbmcgui.Dialog()
        dialog.notification('错误', '获取歌单歌曲失败', xbmcgui.NOTIFICATION_ERROR, 2000, False)
        log('Failed to get playlist all tracks for play all', xbmc.LOGERROR)
        return

    tracks = all_tracks_data.get('songs', [])

    if not tracks:
        dialog = xbmcgui.Dialog()
        dialog.notification('提示', '该歌单暂无歌曲', xbmcgui.NOTIFICATION_INFO, 2000, False)
        log('No tracks found in playlist for play all: %s' % playlist_id)
        return

    # 获取默认音质
    default_quality = get_default_quality()
    log('Using quality: %s' % default_quality)
    log('Total tracks to play: %d' % len(tracks))

    # 构建播放列表
    playlist_items = []

    for track in tracks:
        track_id = track.get('id')
        name = track.get('name', '')
        artists = track.get('ar', [])
        album = track.get('al', {})

        # 提取歌手信息
        artist_names = ', '.join([ar.get('name', '') for ar in artists])

        # 提取专辑信息
        album_name = album.get('name', '')
        pic_id = album.get('picId', 0) or album.get('pic', 0)

        # 获取播放 URL（使用优先级机制：kuwo > joox > netease）
        play_url, actual_source = get_play_url_with_fallback(track_id, default_quality, name, artist_names)

        if not play_url:
            log('Failed to get play URL for track_id=%s from all sources' % track_id, xbmc.LOGWARNING)
            continue

        log('Play URL obtained from %s: %s' % (actual_source, play_url[:80] + '...'))

        # 构建 ListItem
        li = xbmcgui.ListItem(label=name)
        li.setInfo('music', {
            'title': name,
            'artist': artist_names,
            'album': album_name,
        })

        # 设置封面
        if album.get('picUrl'):
            li.setArt({'icon': album['picUrl'], 'thumb': album['picUrl'], 'fanart': album['picUrl']})

        # 设置播放路径
        li.setPath(play_url)

        # 标记为可播放
        li.setProperty('IsPlayable', 'true')

        # 添加到播放列表（使用 URL 和 ListItem）
        playlist_items.append((play_url, li))

    # 播放播放列表
    if playlist_items:
        xbmc.PlayList(xbmc.PLAYLIST_MUSIC).clear()
        for play_url, li in playlist_items:
            xbmc.PlayList(xbmc.PLAYLIST_MUSIC).add(play_url, li)
        xbmc.Player().play(xbmc.PlayList(xbmc.PLAYLIST_MUSIC), startpos=0)
        log('Playlist playback started: %d tracks' % len(playlist_items))
    else:
        log('No tracks to play', xbmc.LOGWARNING)

def add_directory_item(name, url, is_folder=True, icon=None, fanart=None, info=None):
    """Add directory item to Kodi listing"""
    li = xbmcgui.ListItem(name)
    
    # Set icon
    if icon:
        li.setArt({'icon': icon, 'thumb': icon})
    
    # Set fanart (background image)
    if fanart:
        li.setArt({'fanart': fanart})
    
    # Set music metadata using setInfo (compatible with all Kodi versions)
    if info:
        li.setInfo('music', info)
    
    # Mark as playable if not a folder
    if not is_folder:
        li.setProperty('IsPlayable', 'true')
    
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=is_folder)

def validate_query(query):
    """
    Validate search query
    
    Args:
        query: Search query string
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not query:
        return False
    
    # Remove leading/trailing whitespace
    query = query.strip()
    
    # Check if empty after stripping
    if not query:
        return False
    
    # Check minimum length
    if len(query) < 1:
        return False
    
    return True

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


def extract_song_id_from_play_url():
    """
    从当前播放的 URL 中提取歌曲 ID
    
    Returns:
        tuple: (source, track_id) 或 (None, None) 如果提取失败
    """
    # 获取当前播放的 URL
    play_url = xbmc.getInfoLabel('Player.Filenameandpath')
    log('Current play URL: %s' % play_url)
    
    if not play_url:
        return None, None
    
    # 尝试从 plugin.audio.musicGD 的 URL 中提取
    # 格式: plugin://plugin.audio.musicGD/?mode=play&source=netease&id=12345&...
    if 'plugin.audio.musicGD' in play_url:
        try:
            # 解析 URL 参数
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(play_url)
            params = parse_qs(parsed.query)
            
            track_id = params.get('id', [''])[0]
            source = params.get('source', ['netease'])[0]
            
            if track_id:
                log('Extracted from plugin.audio.musicGD: source=%s, track_id=%s' % (source, track_id))
                return source, track_id
        except Exception as e:
            log('Error extracting from plugin.audio.musicGD URL: %s' % str(e), xbmc.LOGERROR)
    
    # 尝试从 plugin.audio.music 的 URL 中提取
    # 格式: plugin://plugin.audio.music/play/song/1811921555/0/0/207/netease/
    elif 'plugin.audio.music' in play_url and '/play/song/' in play_url:
        try:
            parts = play_url.split('/play/song/')
            if len(parts) > 1:
                song_part = parts[1].split('/')[0]
                # 从 URL 路径中提取 source（通常是最后一部分）
                url_parts = play_url.split('/')
                source = url_parts[-1] if len(url_parts) > 0 and url_parts[-1] else 'netease'
                
                log('Extracted from plugin.audio.music: source=%s, track_id=%s' % (source, song_part))
                return source, song_part
        except Exception as e:
            log('Error extracting from plugin.audio.music URL: %s' % str(e), xbmc.LOGERROR)
    
    # 尝试从 URL 中提取 dbid（数据库 ID）
    dbid = xbmc.getInfoLabel('MusicPlayer.Property(dbid)')
    if dbid and dbid != '-1':
        log('Found dbid from MusicPlayer: %s' % dbid)
        # dbid 可能是歌曲的数据库 ID，但我们需要 API ID
        # 这里暂时无法直接转换，返回 None
        pass
    
    return None, None


def main():
    """Main plugin entry point"""

    # 启动时自动清理过期缓存
    try:
        expired_count = clear_expired_cache()
        if expired_count > 0:
            log('Auto-cleared %d expired cache files on startup' % expired_count)
    except Exception as e:
        log('Error auto-clearing expired cache: %s' % str(e), xbmc.LOGERROR)

    # 首先尝试解析 xbmcswift2 风格的 URL 路径
    if len(sys.argv) > 0 and sys.argv[0]:
        # sys.argv[0] 格式: plugin://plugin.audio.musicGD/path
        from urllib.parse import urlparse
        parsed = urlparse(sys.argv[0])
        path = parsed.path
        
        if path and path != '/':
            # 解析 xbmcswift2 路由
            xbmcswift2_params = parse_xbmcswift2_url(path)
            
            if xbmcswift2_params:
                log('Detected xbmcswift2 route: %s' % xbmcswift2_params)
                
                if xbmcswift2_params['mode'] == 'current_song_comments':
                    # 处理当前歌曲评论
                    offset = int(xbmcswift2_params.get('offset', '0'))
                    
                    # 从播放 URL 中提取歌曲 ID
                    source, track_id = extract_song_id_from_play_url()
                    
                    if not track_id:
                        dialog = xbmcgui.Dialog()
                        dialog.notification(
                            '错误',
                            '无法从播放URL提取歌曲ID\n请确保正在播放音乐',
                            xbmcgui.NOTIFICATION_ERROR,
                            3000,
                            False
                        )
                        log('Invalid song_id extracted from play URL', xbmc.LOGERROR)
                        xbmcplugin.endOfDirectory(int(sys.argv[1]))
                        return
                    
                    # 显示评论
                    show_song_comments(source, track_id, offset)
                    xbmcplugin.endOfDirectory(int(sys.argv[1]))
                    return
                
                elif xbmcswift2_params['mode'] == 'comments':
                    # 处理指定歌曲评论
                    source = xbmcswift2_params.get('source', 'netease')
                    track_id = xbmcswift2_params.get('id', '')
                    offset = int(xbmcswift2_params.get('offset', '0'))
                    
                    show_song_comments(source, track_id, offset)
                    xbmcplugin.endOfDirectory(int(sys.argv[1]))
                    return
    
    # 原有的参数解析逻辑（兼容性）
    args = parse_qs(sys.argv[2][1:]) if len(sys.argv) > 2 else {}
    mode = args.get('mode', [''])[0]

    log('Plugin started with mode: %s' % mode if mode else 'main menu')
    log('Full args: %s' % args)

    if mode == 'search':
        search_music()
    elif mode == 'play':
        source = args.get('source', [''])[0]
        track_id = args.get('id', [''])[0]
        pic_id = args.get('pic_id', [''])[0]
        lyric_id = args.get('lyric_id', [''])[0]
        name = args.get('name', [''])[0]
        artist = args.get('artist', [''])[0]
        album = args.get('album', [''])[0]
        play_music(source, track_id, pic_id, lyric_id, name, artist, album)
    elif mode == 'comments':
        source = args.get('source', [''])[0]
        track_id = args.get('id', [''])[0]
        offset = int(args.get('offset', ['0'])[0])
        show_song_comments(source, track_id, offset)
    elif mode == 'playlist_tags':
        show_playlist_tags()
    elif mode == 'highquality_playlists':
        cat = args.get('cat', ['全部'])[0]
        offset = int(args.get('offset', ['0'])[0])
        show_highquality_playlists(cat=cat, offset=offset)
    elif mode == 'playlist_detail':
        playlist_id = args.get('id', [''])[0]
        cat = args.get('cat', ['全部'])[0]
        offset = int(args.get('offset', ['0'])[0])
        show_playlist_detail(playlist_id, cat=cat, offset=offset)
    elif mode == 'play_playlist_all':
        playlist_id = args.get('id', [''])[0]
        cat = args.get('cat', ['全部'])[0]
        offset = int(args.get('offset', ['0'])[0])
        play_playlist_all(playlist_id, cat=cat, offset=offset)
    elif mode == 'cache_management':
        show_cache_management()
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
        return
    else:
        show_main_menu()

    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def show_main_menu():
    """Display main menu"""
    add_directory_item('搜索音乐', get_url(mode='search'), icon=__icon__, fanart=__fanart__)
    add_directory_item('歌单精选', get_url(mode='playlist_tags'), icon=__icon__, fanart=__fanart__)
    add_directory_item('缓存管理', get_url(mode='cache_management'), icon=__icon__, fanart=__fanart__)


def show_cache_management():
    """显示缓存管理界面"""
    log('Showing cache management')

    # 获取缓存统计信息
    cache_info = get_cache_info()

    # 构建缓存信息文本
    info_text = "═══════════════════════════════════════\n"
    info_text += "              缓存统计信息\n"
    info_text += "═══════════════════════════════════════\n\n"

    info_text += f"缓存状态: {'已启用' if __addon__.getSetting('cache_enabled') == 'true' else '已禁用'}\n"
    info_text += f"缓存过期时间: 24 小时\n\n"

    info_text += f"总缓存文件数: {cache_info['total_files']}\n"
    info_text += f"有效缓存文件: {cache_info['valid_files']}\n"
    info_text += f"过期缓存文件: {cache_info['expired_files']}\n"
    info_text += f"缓存总大小: {cache_info['total_size_mb']} MB\n\n"

    info_text += "═══════════════════════════════════════\n"

    # 显示缓存信息
    dialog = xbmcgui.Dialog()
    dialog.textviewer('缓存管理', info_text)

    # 构建操作选项
    options = []

    # 添加"清理过期缓存"选项
    if cache_info['expired_files'] > 0:
        options.append(f'🧹 清理过期缓存 ({cache_info["expired_files"]} 个文件)')

    # 添加"清理所有缓存"选项
    if cache_info['total_files'] > 0:
        options.append(f'🗑️  清理所有缓存 ({cache_info["total_files"]} 个文件)')

    # 添加"刷新缓存信息"选项
    options.append('🔄 刷新缓存信息')

    # 如果有选项,显示选择对话框
    if options:
        # 添加"退出"选项
        options.append('❌ 退出')

        selected = dialog.select('请选择操作', options)

        if selected >= 0:
            action = options[selected]

            # 处理"清理过期缓存"
            if '清理过期缓存' in action:
                log('User selected: Clear expired cache')
                deleted = clear_expired_cache()
                dialog.notification('缓存管理', f'已清理 {deleted} 个过期缓存文件',
                                   xbmcgui.NOTIFICATION_INFO, 3000, False)
                # 重新显示缓存管理界面
                show_cache_management()
                return

            # 处理"清理所有缓存"
            elif '清理所有缓存' in action:
                log('User selected: Clear all cache')

                # 确认对话框
                confirm = dialog.yesno(
                    '确认清理',
                    '确定要清理所有缓存吗?\n\n这将删除所有缓存的歌单、标签和歌曲数据。',
                    yeslabel='确定',
                    nolabel='取消'
                )

                if confirm:
                    deleted = clear_all_cache()
                    dialog.notification('缓存管理', f'已清理 {deleted} 个缓存文件',
                                       xbmcgui.NOTIFICATION_INFO, 3000, False)
                    # 重新显示缓存管理界面
                    show_cache_management()
                    return

            # 处理"刷新缓存信息"
            elif '刷新缓存信息' in action:
                log('User selected: Refresh cache info')
                show_cache_management()
                return

            # 处理"退出"
            elif '退出' in action:
                log('User selected: Exit from cache management')
                return
    else:
        # 没有缓存文件时,只显示"刷新"和"退出"选项
        options = ['🔄 刷新缓存信息', '❌ 退出']
        selected = dialog.select('请选择操作', options)

        if selected >= 0:
            action = options[selected]

            if '刷新缓存信息' in action:
                log('User selected: Refresh cache info')
                show_cache_management()
                return
            elif '退出' in action:
                log('User selected: Exit from cache management')
                return


def search_music():
    """Handle music search"""
    keyboard = xbmc.Keyboard('', '输入搜索关键字')
    keyboard.doModal()
    
    if not keyboard.isConfirmed():
        log('Search cancelled by user')
        return
    
    query = keyboard.getText()
    
    # Validate query
    if not validate_query(query):
        xbmcgui.Dialog().ok(__addon_name__, '搜索关键字不能为空')
        log('Invalid search query: empty or whitespace only')
        return
    
    log('Searching for: %s' % query)

    default_source = get_default_source()
    log('Using music source: %s' % default_source)
    
    # Call API without double encoding
    data = api_call('search', source=default_source, name=query, count='20', pages='1')
    
    if data is None:
        # API call failed
        xbmcgui.Dialog().ok(
            __addon_name__, 
            '搜索失败：API不可用或网络错误。\n\n请检查：\n1. 网络连接是否正常\n2. 音乐源是否可用\n3. 是否达到请求频率限制'
        )
        log('Search failed: API returned None', xbmc.LOGERROR)
        return
    
    if isinstance(data, list) and len(data) == 0:
        # No results found
        xbmcgui.Dialog().ok(
            __addon_name__, 
            '未找到相关结果\n\n建议：\n1. 尝试使用不同的关键字\n2. 检查拼写是否正确\n3. 尝试更换音乐源'
        )
        log('No results found for query: %s' % query, xbmc.LOGINFO)
        return
    
    # Display results (optimized: only display basic info, fetch details on play)
    log('Found %d results' % len(data))
    
    for item in data:
        name = item.get('name', '')
        artist = ', '.join(item.get('artist', []))
        album = item.get('album', '')
        pic_id = item.get('pic_id', '')
        lyric_id = item.get('lyric_id', '')
        track_id = item.get('id', '')
        source = item.get('source', default_source)

        title = '%s - %s' % (artist, name) if artist else name
        # Pass all parameters via URL, fetch details on play
        url = get_url(mode='play', source=source, id=track_id, pic_id=pic_id, lyric_id=lyric_id, name=name, artist=artist, album=album)
        info = {
            'title': name,
            'artist': artist,
            'album': album,
        }
        # Don't fetch icon and fanart during search to speed up
        add_directory_item(title, url, is_folder=False, info=info)
    
    log('Search results displayed successfully')

def play_music(source, track_id, pic_id='', lyric_id='', name='', artist='', album=''):
    """Handle music playback

    Args:
        source: Music source (original source, but will use priority fallback)
        track_id: Track ID
        pic_id: Album picture ID (optional)
        lyric_id: Lyrics ID (optional)
        name: Song name (optional, passed from search)
        artist: Artist name (optional, passed from search)
        album: Album name (optional, passed from search)
    """
    if not track_id:
        log('Invalid play parameters: track_id=%s' % track_id, xbmc.LOGERROR)
        xbmcgui.Dialog().ok(__addon_name__, '播放失败：缺少必要参数')
        return

    log('Playing music: original_source=%s, track_id=%s' % (source, track_id))
    log('Song info: name=%s, artist=%s, album=%s' % (name, artist, album))
    log('Additional params: pic_id=%s, lyric_id=%s' % (pic_id, lyric_id))

    default_quality = get_default_quality()
    log('Using quality: %s' % default_quality)

    # Get play URL with priority fallback (default_source > kuwo > joox > netease)
    play_url, actual_source = get_play_url_with_fallback(track_id, default_quality, name, artist)

    if not play_url:
        # 获取默认音乐源名称
        default_source = get_default_source()
        source_names = {
            'netease': '网易云音乐',
            'kuwo': '酷我音乐',
            'joox': 'JOOX',
            'tencent': '腾讯音乐',
            'tidal': 'Tidal',
            'spotify': 'Spotify',
            'ytmusic': 'YouTube Music',
            'qobuz': 'Qobuz',
            'deezer': 'Deezer',
            'migu': '咪咕音乐',
            'kugou': '酷狗音乐',
            'ximalaya': '喜马拉雅',
            'apple': 'Apple Music'
        }

        # 构建尝试的音乐源列表
        tried_sources = ['默认音乐源 (%s)' % source_names.get(default_source, default_source)]
        for fallback in ['kuwo', 'joox', 'netease']:
            if fallback != default_source:
                tried_sources.append('%s (%s)' % (source_names.get(fallback, fallback), fallback))

        xbmcgui.Dialog().ok(
            __addon__,
            '获取播放链接失败\n\n已尝试以下音乐源：\n%s\n\n可能原因：\n- 歌曲已下架\n- 需要VIP权限\n- 网络连接问题' % '\n'.join(['  %d. %s' % (i+1, s) for i, s in enumerate(tried_sources)])
        )
        log('Failed to get play URL from all sources', xbmc.LOGERROR)
        return

    log('Using source: %s' % actual_source)

    # Create ListItem with proper settings
    li = xbmcgui.ListItem(path=play_url)

    # Set music metadata using actual song info
    li.setInfo('music', {
        'title': name or 'Unknown',
        'artist': artist or 'Unknown',
        'album': album or 'Unknown'
    })

    log('Music metadata set: title=%s, artist=%s, album=%s' % (name, artist, album))

    # Set content type to music
    li.setContentLookup(False)

    # Fetch and set album art if available
    if pic_id:
        album_art_url = get_album_art_url(actual_source, pic_id)
        if album_art_url:
            li.setArt({'thumb': album_art_url, 'icon': album_art_url})
            log('Album art set: %s' % album_art_url[:50] + '...')

    # Fetch and set fanart if available
    if pic_id:
        fanart_url = get_album_art_url(actual_source, pic_id, size='1080')
        if fanart_url:
            li.setArt({'fanart': fanart_url})
            log('Fanart set: %s' % fanart_url[:50] + '...')

    # Mark as playable
    li.setProperty('IsPlayable', 'true')

    log('Calling xbmcplugin.setResolvedUrl')
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)
    log('xbmcplugin.setResolvedUrl called successfully')

    # Cache lyrics in background
    if lyric_id:
        log('Caching lyrics: lyric_id=%s, source=%s' % (lyric_id, actual_source))
        cache_lyrics(actual_source, lyric_id)

def ensure_cache_dir():
    """Ensure cache directory exists"""
    if not xbmcvfs.exists(CACHE_DIR):
        try:
            xbmcvfs.mkdirs(CACHE_DIR)
            log('Cache directory created: %s' % CACHE_DIR)
        except Exception as e:
            log('Failed to create cache directory: %s' % str(e), xbmc.LOGERROR)


# ==================== 缓存管理系统 ====================

def get_cache_key(prefix, *args):
    """
    生成缓存键

    Args:
        prefix: 缓存前缀 (如 'playlist_tags', 'playlists', 'playlist_detail')
        *args: 缓存参数 (如分类、偏移量、ID等)

    Returns:
        str: MD5 缓存键
    """
    cache_string = '%s_%s' % (prefix, '_'.join(str(arg) for arg in args))
    return hashlib.md5(cache_string.encode()).hexdigest()


def is_cache_expired(cache_file):
    """
    检查缓存是否过期

    Args:
        cache_file: 缓存文件路径

    Returns:
        bool: True 表示已过期, False 表示未过期
    """
    try:
        # 检查设置中是否启用缓存
        if __addon__.getSetting('cache_enabled') != 'true':
            return True

        # 获取文件修改时间
        import os
        file_path = xbmcvfs.translatePath(cache_file)
        if not os.path.exists(file_path):
            return True

        file_mtime = os.path.getmtime(file_path)
        current_time = time.time()

        # 检查是否过期
        is_expired = (current_time - file_mtime) > CACHE_EXPIRE_SECONDS

        if is_expired:
            log('Cache expired: %s (age: %d seconds)' % (cache_file, int(current_time - file_mtime)))
        else:
            age = int(current_time - file_mtime)
            log('Cache valid: %s (age: %d seconds, remaining: %d seconds)' %
                (cache_file, age, CACHE_EXPIRE_SECONDS - age))

        return is_expired

    except Exception as e:
        log('Error checking cache expiration: %s' % str(e), xbmc.LOGERROR)
        return True


def get_cached_data(cache_key):
    """
    从缓存读取数据

    Args:
        cache_key: 缓存键

    Returns:
        dict: 缓存数据, 或 None 如果缓存不存在或已过期
    """
    try:
        cache_file = os.path.join(CACHE_DIR, '%s.json' % cache_key)

        # 检查缓存是否存在
        if not xbmcvfs.exists(cache_file):
            log('Cache not found: %s' % cache_key)
            return None

        # 检查缓存是否过期
        if is_cache_expired(cache_file):
            # 删除过期缓存
            xbmcvfs.delete(cache_file)
            log('Deleted expired cache: %s' % cache_key)
            return None

        # 读取缓存数据
        file_path = xbmcvfs.translatePath(cache_file)
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        log('Cache hit: %s' % cache_key)
        return data

    except json.JSONDecodeError as e:
        log('Cache JSON decode error: %s - %s' % (cache_key, str(e)), xbmc.LOGERROR)
        # 删除损坏的缓存文件
        try:
            xbmcvfs.delete(os.path.join(CACHE_DIR, '%s.json' % cache_key))
        except:
            pass
        return None
    except Exception as e:
        log('Error reading cache: %s - %s' % (cache_key, str(e)), xbmc.LOGERROR)
        return None


def set_cached_data(cache_key, data):
    """
    写入缓存数据

    Args:
        cache_key: 缓存键
        data: 要缓存的数据 (必须是 JSON 可序列化的)

    Returns:
        bool: True 表示成功, False 表示失败
    """
    try:
        ensure_cache_dir()

        cache_file = os.path.join(CACHE_DIR, '%s.json' % cache_key)
        file_path = xbmcvfs.translatePath(cache_file)

        # 写入缓存数据
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        log('Cache written: %s' % cache_key)
        return True

    except Exception as e:
        log('Error writing cache: %s - %s' % (cache_key, str(e)), xbmc.LOGERROR)
        return False


def clear_all_cache():
    """
    清理所有缓存

    Returns:
        int: 删除的缓存文件数量
    """
    try:
        ensure_cache_dir()

        cache_path = xbmcvfs.translatePath(CACHE_DIR)
        deleted_count = 0

        # 遍历缓存目录
        if xbmcvfs.exists(CACHE_DIR):
            dirs, files = xbmcvfs.listdir(cache_path)

            for file in files:
                file_path = os.path.join(cache_path, file)
                try:
                    xbmcvfs.delete(file_path)
                    deleted_count += 1
                    log('Deleted cache file: %s' % file)
                except Exception as e:
                    log('Failed to delete cache file %s: %s' % (file, str(e)), xbmc.LOGERROR)

        log('Cache cleared: %d files deleted' % deleted_count)
        return deleted_count

    except Exception as e:
        log('Error clearing cache: %s' % str(e), xbmc.LOGERROR)
        return 0


def clear_expired_cache():
    """
    清理过期缓存

    Returns:
        int: 删除的过期缓存文件数量
    """
    try:
        ensure_cache_dir()

        cache_path = xbmcvfs.translatePath(CACHE_DIR)
        deleted_count = 0

        # 遍历缓存目录
        if xbmcvfs.exists(CACHE_DIR):
            dirs, files = xbmcvfs.listdir(cache_path)

            for file in files:
                file_path = os.path.join(cache_path, file)
                try:
                    # 检查是否过期
                    if is_cache_expired(file_path):
                        xbmcvfs.delete(file_path)
                        deleted_count += 1
                        log('Deleted expired cache: %s' % file)
                except Exception as e:
                    log('Failed to check/delete cache file %s: %s' % (file, str(e)), xbmc.LOGERROR)

        log('Expired cache cleared: %d files deleted' % deleted_count)
        return deleted_count

    except Exception as e:
        log('Error clearing expired cache: %s' % str(e), xbmc.LOGERROR)
        return 0


def get_cache_info():
    """
    获取缓存统计信息

    Returns:
        dict: 包含缓存统计信息的字典
    """
    try:
        ensure_cache_dir()

        cache_path = xbmcvfs.translatePath(CACHE_DIR)
        total_files = 0
        expired_files = 0
        total_size = 0

        if xbmcvfs.exists(CACHE_DIR):
            dirs, files = xbmcvfs.listdir(cache_path)

            for file in files:
                file_path = os.path.join(cache_path, file)
                try:
                    total_files += 1

                    # 检查文件大小
                    stat = xbmcvfs.Stat(file_path)
                    total_size += stat.st_size()

                    # 检查是否过期
                    if is_cache_expired(file_path):
                        expired_files += 1
                except Exception as e:
                    log('Error checking cache file %s: %s' % (file, str(e)), xbmc.LOGERROR)

        return {
            'total_files': total_files,
            'expired_files': expired_files,
            'valid_files': total_files - expired_files,
            'total_size': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2)
        }

    except Exception as e:
        log('Error getting cache info: %s' % str(e), xbmc.LOGERROR)
        return {
            'total_files': 0,
            'expired_files': 0,
            'valid_files': 0,
            'total_size': 0,
            'total_size_mb': 0
        }


# ==================== 原有缓存函数 (保持兼容) ====================

def get_cache_path(filename):
    """Get full cache file path"""
    return os.path.join(CACHE_DIR, filename)

def get_cached_album_art(source, pic_id):
    """Get cached album art or fetch it from API"""
    if __addon__.getSetting('cache_enabled') != 'true':
        # Cache disabled, fetch directly
        return get_album_art_url(source, pic_id)
    
    ensure_cache_dir()
    cache_key = hashlib.md5(('%s_%s' % (source, pic_id)).encode()).hexdigest()
    cache_file = get_cache_path('%s.jpg' % cache_key)
    
    if xbmcvfs.exists(cache_file):
        log('Using cached album art: %s' % cache_key)
        return cache_file
    
    # Fetch and cache album art
    url = get_album_art_url(source, pic_id)
    if url:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            with open(xbmcvfs.translatePath(cache_file), 'wb') as f:
                f.write(response.content)
            log('Album art cached: %s' % cache_key)
            return cache_file
        except Exception as e:
            log('Failed to cache album art: %s' % str(e), xbmc.LOGERROR)
    
    return None

def get_album_art_url(source, pic_id, size='500'):
    """Get album art URL from API
    
    Args:
        source: Music source
        pic_id: Picture ID
        size: Image size (300 or 500, default 500)
    
    Returns:
        str: Album art URL, or None if failed
    """
    data = api_call('pic', source=source, id=pic_id, size=size)
    if data and 'url' in data:
        log('Album art URL obtained (size=%s): %s' % (size, data['url'][:50] + '...'))
        return data['url']
    return None

def cache_lyrics(source, lyric_id):
    """Cache lyrics for a song"""
    if __addon__.getSetting('cache_enabled') != 'true':
        return
    
    ensure_cache_dir()
    data = api_call('lyric', source=source, id=lyric_id)
    
    if data and 'lyric' in data:
        cache_key = hashlib.md5(('%s_%s' % (source, lyric_id)).encode()).hexdigest()
        cache_file = get_cache_path('%s.lrc' % cache_key)
        try:
            with open(xbmcvfs.translatePath(cache_file), 'w', encoding='utf-8') as f:
                f.write(data['lyric'])
            log('Lyrics cached: %s' % cache_key)
        except Exception as e:
            log('Failed to cache lyrics: %s' % str(e), xbmc.LOGERROR)

def get_song_comments(source, track_id, offset=0, limit=50):
    """
    获取歌曲评论
    
    Args:
        source: Music source (e.g., netease)
        track_id: Track ID
        offset: Offset for pagination
        limit: Number of comments per page
    
    Returns:
        dict: Comments data, or None if failed
    """
    log('Getting comments for track_id=%s, offset=%d, limit=%d' % (track_id, offset, limit))
    
    # 只对 netease 音乐源使用评论 API
    if source != 'netease':
        log('Comments not supported for source: %s' % source, xbmc.LOGWARNING)
        return None
    
    try:
        # 使用真实的评论 API
        comment_url = 'https://apis.netstart.cn/music/comment/music'
        params = {
            'id': track_id,
            'limit': limit,
            'offset': offset
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
        
        response = requests.get(comment_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        log('Comments API success: total=%d, hot=%d, comments=%d' % (
            data.get('total', 0),
            len(data.get('hotComments', [])),
            len(data.get('comments', []))
        ))
        
        return data
        
    except requests.RequestException as e:
        log('Error getting comments: %s' % str(e), xbmc.LOGERROR)
        return None
    except Exception as e:
        log('Unexpected error getting comments: %s' % str(e), xbmc.LOGERROR)
        return None

def show_song_comments(source, track_id, offset=0):
    """
    显示歌曲评论（支持分页导航）
    
    Args:
        source: Music source
        track_id: Track ID
        offset: Offset for pagination
    """
    log('Showing comments for track_id=%s, offset=%d' % (track_id, offset))
    
    dialog = xbmcgui.Dialog()
    
    # 验证 track_id
    if not track_id or track_id == 'None' or track_id == '':
        dialog.notification('错误', '无法获取歌曲ID', xbmcgui.NOTIFICATION_ERROR, 3000, False)
        log('Invalid track_id for comments', xbmc.LOGERROR)
        return
    
    # 检查音乐源是否支持评论
    if source != 'netease':
        dialog.textviewer('歌曲评论', '抱歉，当前音乐源不支持评论功能。\n\n评论功能目前仅支持网易云音乐（netease）音乐源。\n\n请在设置中切换到 netease 音乐源。')
        log('Comments not supported for source: %s' % source, xbmc.LOGINFO)
        return
    
    limit = 50
    
    try:
        # 获取评论数据
        comments_data = get_song_comments(source, track_id, offset, limit)
        
        if not comments_data:
            dialog.notification('错误', '获取评论失败', xbmcgui.NOTIFICATION_ERROR, 2000, False)
            log('Failed to get comments data', xbmc.LOGERROR)
            return
        
        # 构建评论内容文本
        text_content = ""
        
        # 获取总数
        total = comments_data.get('total', 0)
        
        # 计算当前页码
        current_page = (offset // limit) + 1
        total_pages = (total + limit - 1) // limit if total > 0 else 1
        
        # 添加标题
        text_content += f"              歌曲评论 (第{current_page}页/共{total_pages}页)\n"
        text_content += f"              总计: {total} 条评论\n"
        text_content += "═══════════════════════════════════════\n"
        
        # 热门评论
        hot_comments = comments_data.get('hotComments', [])
        if hot_comments:
            text_content += "🔥 热门评论\n"
            text_content += "═══════════════════════════════════════\n"
            
            for i, comment in enumerate(hot_comments, 1):
                user = comment.get('user', {})
                nickname = user.get('nickname', '匿名用户')
                content = comment.get('content', '')
                liked_count = comment.get('likedCount', 0)
                time_str = comment.get('timeStr', '')
                
                text_content += f"【{i}】{nickname}\n"
                text_content += f"    {content}\n"
                text_content += f"    👍 {liked_count} 点赞 | {time_str}\n\n"
        
        # 最新评论
        comments = comments_data.get('comments', [])
        if comments:
            text_content += "💬 最新评论\n"
            text_content += "═══════════════════════════════════════\n"
            
            for i, comment in enumerate(comments, 1):
                user = comment.get('user', {})
                nickname = user.get('nickname', '匿名用户')
                content = comment.get('content', '')
                liked_count = comment.get('likedCount', 0)
                time_str = comment.get('timeStr', '')
                
                text_content += f"【{offset + i}】{nickname}\n"
                text_content += f"    {content}\n"
                text_content += f"    👍 {liked_count} 点赞 | {time_str}\n\n"
        
        # 添加分页信息
        current_count = len(hot_comments) + len(comments)
        
        if current_count > 0:
            text_content += "\n"
            text_content += f"已显示: {current_count}/{total} 条评论\n"
            text_content += f"当前页: {current_page}/{total_pages}\n"
            text_content += "═══════════════════════════════════════\n"
        else:
            text_content += "\n"
            text_content += "暂无评论\n"
            text_content += "═══════════════════════════════════════\n"
        
        # 显示评论
        dialog.textviewer('歌曲评论', text_content)
        log('Comments displayed successfully')
        
        # 构建操作按钮列表
        action_list = []
        
        # 添加"返回第一页"按钮（如果不是第一页）
        if current_page > 1:
            action_list.append(f'⬅️  返回第1页')
        
        # 添加"上一页"按钮（如果不是第一页）
        if current_page > 1:
            action_list.append(f'⬅️  上一页 (第{current_page - 1}页)')
        
        # 添加"下一页"按钮（如果有更多评论）
        if current_count < total:
            remaining = total - current_count
            action_list.append(f'➡️  下一页 (第{current_page + 1}页, 剩余{remaining}条)')
        
        # 添加"刷新当前页"按钮
        action_list.append(f'🔄  刷新当前页')
        
        # 如果有操作按钮，显示选择对话框
        if action_list:
            # 添加"退出"按钮
            action_list.append('❌  退出')
            
            # 显示操作选择对话框
            selected = dialog.select('请选择操作', action_list)
            
            # 处理用户选择
            if selected >= 0:
                action = action_list[selected]
                
                # 计算按钮索引（考虑"退出"按钮）
                button_index = selected
                
                # 处理"返回第一页"
                if '返回第1页' in action:
                    log('User selected: Return to first page')
                    show_song_comments(source, track_id, offset=0)
                    return
                
                # 处理"上一页"
                elif '上一页' in action:
                    log('User selected: Previous page')
                    new_offset = max(0, offset - limit)
                    show_song_comments(source, track_id, new_offset)
                    return
                
                # 处理"下一页"
                elif '下一页' in action:
                    log('User selected: Next page')
                    new_offset = offset + limit
                    show_song_comments(source, track_id, new_offset)
                    return
                
                # 处理"刷新当前页"
                elif '刷新当前页' in action:
                    log('User selected: Refresh current page')
                    show_song_comments(source, track_id, offset)
                    return
                
                # 处理"退出"
                elif '退出' in action:
                    log('User selected: Exit')
                    return
        
    except Exception as e:
        log('Error showing comments: %s' % str(e), xbmc.LOGERROR)
        dialog.notification('错误', '显示评论失败', xbmcgui.NOTIFICATION_ERROR, 2000, False)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log('Unhandled exception in main(): %s' % str(e), xbmc.LOGERROR)
        xbmcgui.Dialog().ok(__addon_name__, '插件发生错误：\n%s' % str(e))
