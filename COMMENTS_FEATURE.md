# plugin.audio.musicGD 评论功能移植说明

## 功能概述

已成功将 `plugin.audio.music` 的评论功能移植到 `plugin.audio.musicGD` 插件中。

## 实现的功能

### 1. 评论数据获取 ✅
```python
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
```

### 2. 评论显示功能 ✅
```python
def show_song_comments(source, track_id, offset=0):
    """
    显示歌曲评论
    
    Args:
        source: Music source
        track_id: Track ID
        offset: Offset for pagination
    """
```

### 3. 评论路由支持 ✅
在 `main()` 函数中添加了 `comments` 模式支持：
```python
elif mode == 'comments':
    source = args.get('source', [''])[0]
    track_id = args.get('id', [''])[0]
    offset = int(args.get('offset', ['0'])[0])
    show_song_comments(source, track_id, offset)
```

## 评论功能特性

### 1. 显示格式
- 🔥 热门评论（如果有）
- 💬 最新评论
- 👍 点赞数
- ⏰ 时间信息
- 📊 分页信息

### 2. 评论内容
```
              歌曲评论 (第1页/共5页)
              总计: 250 条评论
═══════════════════════════════════════
🔥 热门评论
═══════════════════════════════════════
【1】用户名
    这首歌太好听了！
    👍 1234 点赞 | 2小时前

💬 最新评论
═══════════════════════════════════════
【1】用户名
    不错的歌曲
    👍 56 点赞 | 30分钟前

已显示: 50/250 条评论
═══════════════════════════════════════
```

## 当前限制

### ⚠️ GD Music API 不支持评论接口

**问题**: GD Music API 目前没有提供评论接口

**当前状态**:
- ✅ 评论功能框架已实现
- ✅ 评论显示逻辑已完成
- ❌ 无法从 GD Music API 获取评论数据

**解决方案**:

#### 方案 1: 使用网易云音乐评论 API（推荐）
如果主要使用 `netease` 音乐源，可以集成网易云音乐的评论 API。

**实现步骤**:
1. 在 `api_call` 函数中添加评论 API 支持
2. 使用网易云音乐的评论接口
3. 只对 `netease` 音乐源启用评论功能

#### 方案 2: 等待 GD Music API 添加评论接口
等待 GD Music API 添加评论功能支持。

#### 方案 3: 集成第三方评论服务
集成其他音乐平台的评论服务。

## 如何使用评论功能

### 方法 1: 通过 URL 直接调用
```
plugin://plugin.audio.musicGD/?mode=comments&source=netease&id=123456&offset=0
```

### 方法 2: 在播放时添加上下文菜单（需要实现）
在播放界面添加"查看评论"按钮，点击后调用评论功能。

### 方法 3: 在搜索结果中添加评论选项（需要实现）
在搜索结果的每首歌曲旁边添加"查看评论"选项。

## 扩展实现建议

### 1. 集成网易云音乐评论 API

如果选择方案 1，可以按以下方式实现：

```python
def get_song_comments(source, track_id, offset=0, limit=50):
    """获取歌曲评论"""
    log('Getting comments for track_id=%s, offset=%d, limit=%d' % (track_id, offset, limit))
    
    # 只对 netease 音乐源使用评论 API
    if source != 'netease':
        log('Comments not supported for source: %s' % source, xbmc.LOGWARNING)
        return None
    
    try:
        # 使用网易云音乐的评论 API
        # 注意：这里需要实际的 API 实现
        # 可以参考 plugin.audio.music 中的实现
        
        # 临时返回示例数据
        return {
            'hotComments': [
                {
                    'user': {'nickname': '示例用户1'},
                    'content': '这是一条热门评论',
                    'likedCount': 100,
                    'timeStr': '1小时前'
                }
            ],
            'comments': [
                {
                    'user': {'nickname': '示例用户2'},
                    'content': '这是一条最新评论',
                    'likedCount': 10,
                    'timeStr': '10分钟前'
                }
            ],
            'total': 2
        }
        
    except Exception as e:
        log('Error getting comments: %s' % str(e), xbmc.LOGERROR)
        return None
```

### 2. 在搜索结果中添加评论选项

修改 `search_music` 函数，为每首歌曲添加评论选项：

```python
# 在搜索结果中添加评论选项
comment_url = get_url(mode='comments', source=source, id=track_id, offset='0')
# 可以在歌曲旁边添加评论按钮
```

### 3. 在播放界面添加评论按钮

修改 `play_music` 函数，添加评论按钮：

```python
# 在播放时添加评论选项
# 可以通过上下文菜单或 OSD 按钮实现
```

## 测试评论功能

### 测试步骤

1. **重启 Kodi**
   - 完全关闭 Kodi 并重新启动

2. **测试评论功能**
   - 方式 1: 直接通过 URL 调用
     ```
     plugin://plugin.audio.musicGD/?mode=comments&source=netease&id=123456&offset=0
     ```
   - 方式 2: 在 Kodi 中手动输入 URL

3. **查看结果**
   - 应该显示评论对话框
   - 如果 API 不支持，会显示"抱歉，当前音乐源不支持评论功能。"

### 预期日志

```
[plugin.audio.musicGD] Plugin started with mode: comments
[plugin.audio.musicGD] Full args: {'mode': ['comments'], 'source': ['netease'], 'id': ['123456'], 'offset': ['0']}
[plugin.audio.musicGD] Showing comments for track_id=123456, offset=0
[plugin.audio.musicGD] Getting comments for track_id=123456, offset=0, limit=50
[plugin.audio.musicGD] Comments API not available for this source
[plugin.audio.musicGD] Comments not supported for this source
```

## 版本信息

- **版本**: v1.8.0
- **更新日期**: 2026-01-25
- **新增功能**:
  - ✅ 评论功能框架
  - ✅ 评论显示逻辑
  - ✅ 评论路由支持
  - ⚠️ GD Music API 不支持评论接口

## 未来计划

1. **集成网易云音乐评论 API**
   - 只对 netease 音乐源启用
   - 提供真实的评论数据

2. **改进用户体验**
   - 在搜索结果中添加评论按钮
   - 在播放界面添加评论选项
   - 支持评论分页

3. **扩展到其他音乐源**
   - 等待其他音乐源支持评论
   - 或集成第三方评论服务

## 总结

评论功能已成功移植到 `plugin.audio.musicGD` 插件中，但由于 GD Music API 目前不支持评论接口，该功能暂时无法获取真实的评论数据。

**建议**:
- 如果主要使用网易云音乐，可以集成网易云音乐的评论 API
- 或者等待 GD Music API 添加评论功能支持
- 当前的评论功能框架已经完成，只需要接入真实的评论数据即可

---

**评论功能移植完成！**
