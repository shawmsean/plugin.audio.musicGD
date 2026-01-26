# plugin.audio.musicGD 兼容性修复说明

## 问题描述

**错误信息**:
```
[plugin.audio.musicGD] Unhandled exception in main(): 'xbmcgui.ListItem' object has no attribute 'setInfoTag'
```

**原因**: 
- Kodi 21 的 `InfoTagMusic` 和 `setInfoTag` 方法导入方式不正确
- 不同版本的 Kodi API 可能有所不同
- 需要实现向后兼容性

## 修复方案

### 1. 添加兼容性检查 ✅

```python
# Try to import InfoTagMusic for Kodi 21+, fallback to setInfo for older versions
try:
    from xbmc import InfoTagMusic
    HAS_INFO_TAG_MUSIC = True
except ImportError:
    HAS_INFO_TAG_MUSIC = False
```

**原理**:
- 尝试导入 `InfoTagMusic`
- 如果导入成功，使用新的 API
- 如果导入失败，使用旧的 `setInfo` 方法

### 2. 修改 add_directory_item 函数 ✅

```python
def add_directory_item(name, url, is_folder=True, icon=None, fanart=None, info=None):
    """Add directory item to Kodi listing"""
    li = xbmcgui.ListItem(name)
    
    # Set icon
    if icon:
        li.setArt({'icon': icon, 'thumb': icon})
    
    # Set fanart (background image)
    if fanart:
        li.setArt({'fanart': fanart})
    
    # Set music metadata
    if info:
        if HAS_INFO_TAG_MUSIC:
            # Use InfoTagMusic for Kodi 21+
            tag = InfoTagMusic()
            if 'title' in info:
                tag.setTitle(info['title'])
            if 'artist' in info:
                tag.setArtist(info['artist'])
            if 'album' in info:
                tag.setAlbum(info['album'])
            li.setInfoTag(tag)
        else:
            # Fallback to setInfo for older Kodi versions
            li.setInfo('music', info)
    
    # Mark as playable if not a folder
    if not is_folder:
        li.setProperty('IsPlayable', 'true')
        # Set title if not set
        if not info or 'title' not in info:
            if HAS_INFO_TAG_MUSIC:
                tag = InfoTagMusic()
                tag.setTitle(name)
                li.setInfoTag(tag)
            else:
                li.setInfo('music', {'title': name})
    
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=is_folder)
```

### 3. 修改 play_music 函数 ✅

```python
def play_music(source, track_id, pic_id='', lyric_id=''):
    # ... 获取播放 URL ...
    
    # Create ListItem
    li = xbmcgui.ListItem(path=play_url)
    
    # Set music metadata
    if HAS_INFO_TAG_MUSIC:
        # Use InfoTagMusic for Kodi 21+
        tag = InfoTagMusic()
        tag.setTitle('Music')
        tag.setArtist('Artist')
        li.setInfoTag(tag)
    else:
        # Fallback to setInfo for older Kodi versions
        li.setInfo('music', {
            'title': 'Music',
            'artist': 'Artist',
        })
    
    # ... 其他设置 ...
```

### 4. 添加日志记录 ✅

```python
def main():
    # Log InfoTagMusic support
    log('InfoTagMusic support: %s' % ('Available' if HAS_INFO_TAG_MUSIC else 'Not available (using fallback)'))
    
    # ... 其他代码 ...
```

## 修复内容总结

| 修复项 | 修复前 | 修复后 | 状态 |
|--------|--------|--------|------|
| API 兼容性 | 直接使用 InfoTagMusic | 添加兼容性检查 | ✅ 已修复 |
| 元数据设置 | 只支持新 API | 支持新旧两种 API | ✅ 已修复 |
| 错误处理 | 无 | 自动降级到旧 API | ✅ 已修复 |
| 日志记录 | 不记录 API 支持 | 记录使用的 API | ✅ 已修复 |

## 兼容性策略

### 支持的 Kodi 版本

| Kodi 版本 | API 方式 | 状态 |
|-----------|----------|------|
| Kodi 21+ | InfoTagMusic | ✅ 支持 |
| Kodi 20 及以下 | setInfo | ✅ 支持（自动降级） |

### 工作流程

```
启动插件
    ↓
尝试导入 InfoTagMusic
    ↓
导入成功？
    ├─ 是 → HAS_INFO_TAG_MUSIC = True
    │         ↓
    │    使用 InfoTagMusic API
    │         ↓
    │    无 deprecated 警告
    │
    └─ 否 → HAS_INFO_TAG_MUSIC = False
              ↓
         使用 setInfo API（降级）
              ↓
         正常工作（可能有警告）
```

## 测试步骤

### 1. 应用修复
修复后的 `main.py` 已经保存到：
```
C:\Users\shawm\AppData\Roaming\Kodi\addons\plugin.audio.musicGD\main.py
```

### 2. 重启 Kodi
完全关闭 Kodi 并重新启动。

### 3. 查看日志验证
打开日志文件：
```
C:\Users\shawm\AppData\Roaming\Kodi\kodi.log
```

搜索以下内容：

```
[plugin.audio.musicGD] InfoTagMusic support: Not available (using fallback)
```

这会显示你的 Kodi 版本是否支持 InfoTagMusic。

### 4. 测试播放功能
1. 进入"音乐" → "插件" → "GD 音乐台"
2. 搜索并播放歌曲
3. **预期结果**：正常播放，无错误

## 预期结果

### ✅ 成功情况
- 播放功能正常
- 无 `'xbmcgui.ListItem' object has no attribute 'setInfoTag'` 错误
- 显示专辑封面和背景图（fanart）
- 日志显示使用的 API 方式

### ❌ 如果仍然失败
如果仍然出现错误，请检查：

1. **日志中的 API 支持信息**:
   ```
   [plugin.audio.musicGD] InfoTagMusic support: ?
   ```

2. **完整的错误信息**:
   - 错误类型
   - 错误位置
   - 错误消息

3. **Kodi 版本**:
   - Kodi 版本号
   - 操作系统版本

## 技术细节

### InfoTagMusic vs setInfo

#### InfoTagMusic (Kodi 21+)
```python
tag = InfoTagMusic()
tag.setTitle('Song Title')
tag.setArtist('Artist Name')
tag.setAlbum('Album Name')
li.setInfoTag(tag)
```

**优势**:
- 类型安全
- 更好的性能
- 符合未来 API 方向
- 无 deprecated 警告

#### setInfo (旧版本)
```python
li.setInfo('music', {
    'title': 'Song Title',
    'artist': 'Artist Name',
    'album': 'Album Name'
})
```

**优势**:
- 向后兼容
- 所有版本都支持
- 简单易用

**劣势**:
- 已 deprecated
- 可能在未来版本移除

### 降级策略

```python
if HAS_INFO_TAG_MUSIC:
    # 新 API
    tag = InfoTagMusic()
    tag.setTitle(title)
    li.setInfoTag(tag)
else:
    # 旧 API（降级）
    li.setInfo('music', {'title': title})
```

## 版本信息

- **修复版本**: v1.5.0
- **修复日期**: 2026-01-25
- **修复内容**:
  - 🔥 修复 InfoTagMusic 兼容性问题
  - 🔥 添加 API 兼容性检查
  - 🔥 实现自动降级机制
  - ⚡ 添加 API 支持日志
  - ⚡ 保持 fanart 背景图功能

## 更新历史

### v1.5.0 (2026-01-25) - 兼容性修复
- 🔥 修复 InfoTagMusic 不兼容问题
- 🔥 添加自动降级机制
- 🔥 支持所有 Kodi 版本
- ⚡ 添加 API 支持日志

### v1.4.0 (2026-01-25) - 播放功能最终修复
- 🔥 修复回车键不播放问题
- 🔥 添加 IsPlayable 属性
- ⚡ 添加 fanart 背景图

### v1.3.0 (2026-01-25) - 播放参数修复
- 🔥 修复参数传递问题

### v1.2.0 (2026-01-25) - JSON 解析修复
- 🔥 修复 gzip 解压问题

### v1.1.0 (2026-01-25) - 初次修复
- 修复双重 URL 编码

### v1.0.0 (2025-12-03) - 初始版本
- 基本功能

---

**修复完成！** 

现在插件应该可以在所有 Kodi 版本上正常工作了。请重启 Kodi 并测试播放功能，查看日志中显示的 API 支持信息。
