# plugin.audio.musicGD 播放功能修复说明

## 问题描述

**症状**: 点击搜索结果中的歌曲时，弹出搜索窗口而不是播放歌曲。

**原因分析**:

### 1. 参数传递问题 🔴
在 `play_music` 函数中，使用了错误的方式获取参数：
```python
# 修复前（错误）
def play_music(source, track_id):
    # ...
    args = parse_qs(sys.argv[2][1:])  # ❌ 错误：在播放时重新解析 sys.argv
    pic_id = args.get('pic_id', [''])[0]
    lyric_id = args.get('lyric_id', [''])[0]
```

**问题**:
- 当用户点击搜索结果时，Kodi 会重新调用插件
- 此时 `sys.argv[2]` 的内容可能不正确或为空
- 导致无法获取 `pic_id` 和 `lyric_id` 参数
- 参数缺失可能导致播放失败或触发其他错误

### 2. 函数签名问题 🔴
```python
# 修复前
def play_music(source, track_id):
    # 缺少 pic_id 和 lyric_id 参数
```

**问题**:
- 函数签名只有 `source` 和 `track_id` 两个参数
- 但是在 `search_music` 中构建的 URL 包含了 `pic_id` 和 `lyric_id`
- 参数不匹配导致无法正确传递这些参数

## 修复方案

### 1. 修改函数签名 ✅
```python
# 修复后
def play_music(source, track_id, pic_id='', lyric_id=''):
    """Handle music playback
    
    Args:
        source: Music source (e.g., netease, kuwo)
        track_id: Track ID
        pic_id: Album picture ID (optional)
        lyric_id: Lyrics ID (optional)
    """
```

### 2. 在 main 函数中正确传递参数 ✅
```python
# 修复后
def main():
    """Main plugin entry point"""
    args = parse_qs(sys.argv[2][1:]) if len(sys.argv) > 2 else {}
    mode = args.get('mode', [''])[0]

    log('Plugin started with mode: %s' % mode if mode else 'main menu')
    log('Full args: %s' % args)  # 添加完整参数日志

    if mode == 'search':
        search_music()
    elif mode == 'play':
        # 从 args 中获取所有参数
        source = args.get('source', [''])[0]
        track_id = args.get('id', [''])[0]
        pic_id = args.get('pic_id', [''])[0]
        lyric_id = args.get('lyric_id', [''])[0]
        # 传递所有参数
        play_music(source, track_id, pic_id, lyric_id)
    else:
        show_main_menu()

    xbmcplugin.endOfDirectory(int(sys.argv[1]))
```

### 3. 移除错误的参数解析 ✅
```python
# 修复后
def play_music(source, track_id, pic_id='', lyric_id=''):
    """Handle music playback"""
    if not source or not track_id:
        log('Invalid play parameters: source=%s, track_id=%s' % (source, track_id), xbmc.LOGERROR)
        xbmcgui.Dialog().ok(__addon_name__, '播放失败：缺少必要参数')
        return
    
    # 直接使用函数参数，不再重新解析 sys.argv
    log('Playing music: source=%s, track_id=%s' % (source, track_id))
    log('Additional params: pic_id=%s, lyric_id=%s' % (pic_id, lyric_id))
    
    # ... 其他代码
    
    # 使用函数参数而不是重新解析
    if pic_id:
        album_art_url = get_album_art_url(source, pic_id)
        # ...
    
    if lyric_id:
        cache_lyrics(source, lyric_id)
```

## 修复内容总结

| 问题 | 修复前 | 修复后 | 状态 |
|------|--------|--------|------|
| 函数签名 | `play_music(source, track_id)` | `play_music(source, track_id, pic_id='', lyric_id='')` | ✅ 已修复 |
| 参数获取 | 在函数内重新解析 `sys.argv` | 在 main 函数中从 args 获取并传递 | ✅ 已修复 |
| 参数传递 | 只传递 source 和 track_id | 传递所有参数（source, track_id, pic_id, lyric_id） | ✅ 已修复 |
| 日志记录 | 不完整 | 添加完整的参数日志 | ✅ 已修复 |

## 测试步骤

### 1. 应用修复
修复后的 `main.py` 已经保存到：
```
C:\Users\shawm\AppData\Roaming\Kodi\addons\plugin.audio.musicGD\main.py
```

### 2. 重启 Kodi
完全关闭 Kodi 并重新启动。

### 3. 测试完整流程
1. 进入"音乐" → "插件" → "GD 音乐台"
2. 点击"搜索音乐"
3. 输入：`晴天`
4. 点击确认
5. 查看搜索结果
6. 点击任意一首歌曲（如"晴天(深情版)"）
7. **预期结果**：歌曲开始播放

### 4. 检查日志
打开日志文件：
```
C:\Users\shawm\AppData\Roaming\Kodi\kodi.log
```

搜索以下内容：

#### 搜索阶段日志
```
[plugin.audio.musicGD] Plugin started with mode: search
[plugin.audio.musicGD] Searching for: 晴天
[plugin.audio.musicGD] Using music source: netease
[plugin.audio.musicGD] API Request: https://music-api.gdstudio.xyz/api.php?...
[plugin.audio.musicGD] API success on attempt 1
[plugin.audio.musicGD] API returned 20 items
[plugin.audio.musicGD] Found 20 results
[plugin.audio.musicGD] Search results displayed successfully
```

#### 播放阶段日志
```
[plugin.audio.musicGD] Plugin started with mode: play
[plugin.audio.musicGD] Full args: {'mode': ['play'], 'source': ['netease'], 'id': ['2652820720'], 'pic_id': ['109951170218252280'], 'lyric_id': ['2652820720']}
[plugin.audio.musicGD] Playing music: source=netease, track_id=2652820720
[plugin.audio.musicGD] Additional params: pic_id=109951170218252280, lyric_id=2652820720
[plugin.audio.musicGD] Using quality: 320
[plugin.audio.musicGD] API Request: https://music-api.gdstudio.xyz/api.php?...
[plugin.audio.musicGD] API success on attempt 1
[plugin.audio.musicGD] Play URL obtained: https://m701.music.126.net/...
[plugin.audio.musicGD] Album art set: https://p2.music.126.net/...
[plugin.audio.musicGD] Music playback started
[plugin.audio.musicGD] Caching lyrics: lyric_id=2652820720
```

## 预期行为

### ✅ 正常播放流程
1. 用户点击搜索结果
2. Kodi 调用插件，URL 包含所有参数
3. main 函数解析参数并调用 play_music
4. play_music 获取播放 URL
5. Kodi 开始播放音乐
6. 后台缓存歌词和专辑封面

### ❌ 如果仍然失败
如果点击后仍然弹出搜索窗口，请检查：

1. **参数是否正确传递**
   - 查看日志中的 `Full args` 部分
   - 确认包含 `mode=play` 和其他参数

2. **URL 格式是否正确**
   - 查看日志中的 `API Request` 部分
   - 确认 URL 格式正确

3. **是否有错误信息**
   - 查看日志中的错误信息
   - 确认没有 Python 异常

## 常见问题

### Q1: 点击后没有任何反应
**A**: 检查日志中是否有以下内容：
- `[plugin.audio.musicGD] Playing music:`
- `[plugin.audio.musicGD] Invalid play parameters`

如果没有，说明参数没有正确传递。

### Q2: 点击后弹出错误提示
**A**: 查看错误提示的具体内容：
- "播放失败：缺少必要参数" → 参数传递失败
- "获取播放链接失败" → API 调用失败
- "播放链接不可用" → 歌曲已下架

### Q3: 播放时没有声音
**A**: 可能的原因：
1. 播放 URL 已过期
2. 音频格式不支持
3. 音频设备问题

## 技术细节

### Kodi 插件参数传递机制

1. **搜索阶段**:
   - 用户输入搜索关键字
   - 插件调用 API 获取结果
   - 为每个结果创建列表项
   - 列表项的 URL 包含播放参数：
     ```python
     url = get_url(mode='play', source=source, id=track_id, pic_id=pic_id, lyric_id=lyric_id)
     ```

2. **播放阶段**:
   - 用户点击列表项
   - Kodi 调用插件，传递 URL 中的参数
   - `sys.argv[2]` 包含编码的参数字符串
   - 使用 `parse_qs` 解析参数
   - 调用相应的处理函数

### 修复的关键点

1. **参数完整性**:
   - 确保所有必需的参数都传递
   - 包括 `source`, `id`, `pic_id`, `lyric_id`

2. **参数获取时机**:
   - 在 `main` 函数中获取参数
   - 通过函数参数传递，而不是在函数内重新解析

3. **函数签名匹配**:
   - 函数签名与调用方式匹配
   - 避免参数丢失

## 版本信息

- **修复版本**: v1.3.0
- **修复日期**: 2026-01-25
- **修复内容**:
  - 🔥 修复播放功能参数传递问题
  - 🔥 修改 play_music 函数签名
  - 🔥 在 main 函数中正确传递所有参数
  - ⚡ 添加完整的参数日志

## 更新历史

### v1.3.0 (2026-01-25) - 播放功能修复
- 🔥 修复点击搜索结果后弹出搜索窗口的问题
- 🔥 修复参数传递不完整的问题
- ⚡ 添加完整的参数日志
- ⚡ 改进错误处理

### v1.2.0 (2026-01-25) - JSON 解析修复
- 🔥 修复 gzip 解压缩导致的 JSON 解析失败
- 🔥 移除 Accept-Encoding 请求头
- ⚡ 简化 HTTP 请求头
- ⚡ 添加详细的响应日志

### v1.1.0 (2026-01-25) - 初次修复
- 修复双重 URL 编码问题
- 改进错误处理逻辑
- 添加调试日志

### v1.0.0 (2025-12-03) - 初始版本
- 基本搜索、播放、缓存功能

---

**修复完成！** 请重启 Kodi 并测试播放功能。
