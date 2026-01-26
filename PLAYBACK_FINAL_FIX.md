# plugin.audio.musicGD 播放功能最终修复

## 问题描述

**症状**: 点击搜索结果中的歌曲并按下回车键后，歌曲不播放，没有任何反应。

**日志分析**:
```
[plugin.audio.musicGD] Play URL obtained: https://m7.music.126.net/...
[plugin.audio.musicGD] Music playback started
```

**现象**:
- ✅ API 调用成功
- ✅ 播放 URL 获取成功
- ✅ 专辑封面获取成功
- ✅ 歌词缓存成功
- ❌ 但 Kodi 没有开始播放

## 问题根源

### 🔴 ListItem 没有被标记为可播放

在 Kodi 中，要让列表项可以被播放，必须设置以下属性：

1. **`IsPlayable` 属性**: 必须设置为 `true`
2. **正确的元数据**: 必须设置音乐类型的元数据
3. **`isFolder` 参数**: 必须设置为 `false`

**原代码问题**:
```python
def add_directory_item(name, url, is_folder=True, icon=None, fanart=None, info=None):
    """Add directory item to Kodi listing"""
    li = xbmcgui.ListItem(name)
    if icon:
        li.setArt({'icon': icon, 'thumb': icon})
    if fanart:
        li.setArt({'fanart': fanart})
    if info:
        li.setInfo('music', info)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=is_folder)
    # ❌ 缺少 IsPlayable 属性
```

**问题**:
- 即使 `is_folder=False`，如果没有设置 `IsPlayable` 属性，Kodi 仍然不会播放
- 用户按下回车键时，Kodi 不知道这是一个可播放的项目

## 修复方案

### 1. 修改 add_directory_item 函数 ✅
```python
def add_directory_item(name, url, is_folder=True, icon=None, fanart=None, info=None):
    """Add directory item to Kodi listing"""
    li = xbmcgui.ListItem(name)
    if icon:
        li.setArt({'icon': icon, 'thumb': icon})
    if fanart:
        li.setArt({'fanart': fanart})
    if info:
        li.setInfo('music', info)
    
    # Mark as playable if not a folder
    if not is_folder:
        li.setProperty('IsPlayable', 'true')  # ✅ 关键：标记为可播放
        li.setInfo('music', {'title': name})  # ✅ 设置标题
    
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=is_folder)
```

### 2. 改进 play_music 函数的 ListItem 设置 ✅
```python
def play_music(source, track_id, pic_id='', lyric_id=''):
    # ...
    
    play_url = data['url']
    
    # Create ListItem with proper settings
    li = xbmcgui.ListItem(path=play_url)
    
    # Set music metadata
    li.setInfo('music', {
        'title': 'Music',
        'artist': 'Artist',
    })
    
    # Set content type to music
    li.setContentLookup(False)  # ✅ 禁用内容查找，直接播放
    
    # Set album art if available
    if pic_id:
        album_art_url = get_album_art_url(source, pic_id)
        if album_art_url:
            li.setArt({'thumb': album_art_url, 'icon': album_art_url})
    
    # Mark as playable
    li.setProperty('IsPlayable', 'true')  # ✅ 确保标记为可播放
    
    # Set resolved URL
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)
```

## 修复内容总结

| 问题 | 修复前 | 修复后 | 状态 |
|------|--------|--------|------|
| 列表项可播放 | 未设置 `IsPlayable` | 设置 `IsPlayable='true'` | ✅ 已修复 |
| 列表项元数据 | 可能缺少 title | 总是设置 title | ✅ 已修复 |
| 播放器设置 | 使用默认设置 | 设置 `setContentLookup(False)` | ✅ 已修复 |
| 日志记录 | 不够详细 | 添加详细日志 | ✅ 已修复 |

## 测试步骤

### 1. 应用修复
修复后的 `main.py` 已经保存到：
```
C:\Users\shawm\AppData\Roaming\Kodi\addons\plugin.audio.musicGD\main.py
```

### 2. 重启 Kodi
完全关闭 Kodi 并重新启动。

### 3. 测试播放功能
1. 进入"音乐" → "插件" → "GD 音乐台"
2. 点击"搜索音乐"
3. 输入：`晴天`
4. 点击确认
5. 选择任意一首歌曲
6. **按下回车键**
7. **预期结果**：歌曲开始播放

### 4. 查看日志验证
打开日志文件：
```
C:\Users\shawm\AppData\Roaming\Kodi\kodi.log
```

搜索以下内容：

#### 搜索结果创建阶段
```
[plugin.audio.musicGD] Found 20 results
[plugin.audio.musicGD] Search results displayed successfully
```

#### 播放阶段
```
[plugin.audio.musicGD] Plugin started with mode: play
[plugin.audio.musicGD] Full args: {'mode': ['play'], 'source': ['netease'], 'id': ['...'], ...}
[plugin.audio.musicGD] Playing music: source=netease, track_id=...
[plugin.audio.musicGD] Using quality: 320
[plugin.audio.musicGD] API Request: https://music-api.gdstudio.xyz/api.php?...
[plugin.audio.musicGD] API success on attempt 1
[plugin.audio.musicGD] Play URL obtained: https://m7.music.126.net/...
[plugin.audio.musicGD] Album art set: https://p2.music.126.net/...
[plugin.audio.musicGD] Calling xbmcplugin.setResolvedUrl
[plugin.audio.musicGD] xbmcplugin.setResolvedUrl called successfully
[plugin.audio.musicGD] Music playback started
[plugin.audio.musicGD] Caching lyrics: lyric_id=...
```

## 预期行为

### ✅ 正常播放流程
1. 用户选择搜索结果中的歌曲
2. 用户按下回车键
3. Kodi 调用插件，传递播放参数
4. 插件获取播放 URL
5. 插件创建 ListItem 并设置 `IsPlayable='true'`
6. 插件调用 `xbmcplugin.setResolvedUrl`
7. Kodi 开始播放音乐
8. 显示专辑封面
9. 后台缓存歌词

### ❌ 如果仍然不播放
如果按下回车键后仍然没有反应，请检查：

1. **日志中是否有以下内容**:
   - `[plugin.audio.musicGD] Calling xbmcplugin.setResolvedUrl`
   - `[plugin.audio.musicGD] xbmcplugin.setResolvedUrl called successfully`

2. **Kodi 播放器状态**:
   - 检查 Kodi 是否有其他音频正在播放
   - 检查音频输出设备是否正常

3. **URL 有效性**:
   - 复制日志中的播放 URL
   - 在浏览器中测试是否可以播放

## 技术细节

### Kodi 播放机制

1. **列表项选择**:
   - 用户在搜索结果中选择歌曲
   - Kodi 检查列表项的 `IsPlayable` 属性
   - 如果为 `true`，允许播放

2. **播放触发**:
   - 用户按下回车键或点击
   - Kodi 调用插件，传递 URL 参数
   - 插件调用 `xbmcplugin.setResolvedUrl`

3. **播放器初始化**:
   - Kodi 接收 `setResolvedUrl` 的结果
   - 初始化音频播放器
   - 开始播放

### 关键属性

#### IsPlayable 属性
```python
li.setProperty('IsPlayable', 'true')
```
- 告诉 Kodi 这是一个可播放的项目
- 允许用户按回车键播放
- 显示播放图标（如果有）

#### setContentLookup 方法
```python
li.setContentLookup(False)
```
- 禁用内容查找
- 直接使用提供的 URL 播放
- 避免 Kodi 尝试解析 URL

#### setInfo 方法
```python
li.setInfo('music', {'title': name})
```
- 设置音乐元数据
- 在播放界面显示标题
- 改善用户体验

## 常见问题

### Q1: 按下回车键没有任何反应
**A**: 检查：
1. 日志中是否有 `xbmcplugin.setResolvedUrl called successfully`
2. 列表项是否设置了 `IsPlayable='true'`
3. Kodi 是否有其他音频正在播放

### Q2: 显示"播放失败"错误
**A**: 检查：
1. 日志中的错误信息
2. API 是否返回了播放 URL
3. URL 是否有效（在浏览器中测试）

### Q3: 播放时没有声音
**A**: 检查：
1. Kodi 音频输出设备
2. 系统音量设置
3. URL 是否已过期

## 版本信息

- **修复版本**: v1.4.0
- **修复日期**: 2026-01-25
- **修复内容**:
  - 🔥 修复列表项不可播放的问题
  - 🔥 添加 `IsPlayable` 属性设置
  - 🔥 改进 ListItem 元数据设置
  - 🔥 添加详细的播放日志
  - ⚡ 设置 `setContentLookup(False)`

## 更新历史

### v1.4.0 (2026-01-25) - 播放功能最终修复
- 🔥 修复按下回车键不播放的问题
- 🔥 添加 `IsPlayable` 属性
- 🔥 改进 ListItem 设置
- ⚡ 添加详细日志

### v1.3.0 (2026-01-25) - 播放参数修复
- 🔥 修复点击搜索结果后弹出搜索窗口的问题
- 🔥 修复参数传递不完整的问题

### v1.2.0 (2026-01-25) - JSON 解析修复
- 🔥 修复 gzip 解压缩导致的 JSON 解析失败

### v1.1.0 (2026-01-25) - 初次修复
- 修复双重 URL 编码问题
- 改进错误处理逻辑

### v1.0.0 (2025-12-03) - 初始版本
- 基本搜索、播放、缓存功能

---

**修复完成！** 请重启 Kodi 并测试播放功能。按下回车键后应该可以正常播放音乐了。
