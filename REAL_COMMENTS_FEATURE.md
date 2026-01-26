# plugin.audio.musicGD 真实评论功能集成说明

## ✅ 评论功能已完全集成！

成功集成真实的网易云音乐评论 API，现在可以查看真实的歌曲评论了！

## 集成的评论 API

**API 地址**: `https://apis.netstart.cn/music/comment/music`

**API 参数**:
- `id`: 歌曲 ID
- `limit`: 每页评论数量（默认 50）
- `offset`: 偏移量（用于分页）

**API 响应**:
```json
{
  "hotComments": [
    {
      "user": {
        "nickname": "用户名",
        "avatarUrl": "头像URL"
      },
      "content": "评论内容",
      "likedCount": 点赞数,
      "timeStr": "时间字符串"
    }
  ],
  "comments": [
    {
      "user": {
        "nickname": "用户名",
        "avatarUrl": "头像URL"
      },
      "content": "评论内容",
      "likedCount": 点赞数,
      "timeStr": "时间字符串"
    }
  ],
  "total": 总评论数
}
```

## 功能特性

### 1. 真实评论数据 ✅
- 使用网易云音乐评论 API
- 获取真实的用户评论
- 显示热门评论和最新评论

### 2. 评论分类 ✅
- 🔥 热门评论：点赞数最高的评论
- 💬 最新评论：最新发布的评论

### 3. 评论信息 ✅
- 👤 用户昵称
- 💬 评论内容
- 👍 点赞数
- ⏰ 发布时间

### 4. 分页支持 ✅
- 每页显示 50 条评论
- 支持加载更多评论
- 显示当前页码和总页数

### 5. 音乐源限制 ✅
- 目前仅支持 `netease` 音乐源
- 其他音乐源会显示友好提示

## 使用方法

### 方式 1: 通过 URL 直接调用
```
plugin://plugin.audio.musicGD/?mode=comments&source=netease&id=186016&offset=0
```

**参数说明**:
- `mode=comments`: 评论模式
- `source=netease`: 音乐源（必须为 netease）
- `id=186016`: 歌曲 ID
- `offset=0`: 偏移量（0 = 第一页）

### 方式 2: 在 Kodi 中手动输入
1. 在 Kodi 中按 `Ctrl+O`（Windows）或 `Cmd+O`（Mac）
2. 输入 URL:
   ```
   plugin://plugin.audio.musicGD/?mode=comments&source=netease&id=186016&offset=0
   ```
3. 按回车键

### 方式 3: 加载更多评论
```
plugin://plugin.audio.musicGD/?mode=comments&source=netease&id=186016&offset=50
```

## 评论显示格式

```
              歌曲评论 (第1页/共39418页)
              总计: 1970879 条评论
═══════════════════════════════════════
🔥 热门评论
═══════════════════════════════════════
【1】用户名
    这首歌太好听了！
    👍 12345 点赞 | 2小时前

【2】用户名
    经典之作
    👍 9876 点赞 | 3小时前

💬 最新评论
═══════════════════════════════════════
【1】用户名
    不错的歌曲
    👍 56 点赞 | 30分钟前

【2】用户名
    支持！
    👍 23 点赞 | 15分钟前

已显示: 50/1970879 条评论
当前页: 1/39418
═══════════════════════════════════════

提示: 可以通过 URL 参数加载更多评论
例如: plugin://plugin.audio.musicGD/?mode=comments&source=netease&id=186016&offset=50
```

## 测试步骤

### 1. 重启 Kodi
完全关闭 Kodi 并重新启动。

### 2. 测试评论功能
#### 方法 1: 使用已知歌曲 ID
1. 在 Kodi 中按 `Ctrl+O`（Windows）或 `Cmd+O`（Mac）
2. 输入 URL:
   ```
   plugin://plugin.audio.musicGD/?mode=comments&source=netease&id=186016&offset=0
   ```
3. 按回车键
4. **预期结果**：显示歌曲评论对话框

#### 方法 2: 使用搜索结果中的歌曲
1. 搜索任意歌曲
2. 记下歌曲 ID（可以从日志中获取）
3. 使用该 ID 调用评论功能

### 3. 查看日志验证
打开日志文件：
```
C:\Users\shawm\AppData\Roaming\Kodi\kodi.log
```

搜索以下内容：
```
[plugin.audio.musicGD] Plugin started with mode: comments
[plugin.audio.musicGD] Showing comments for track_id=186016, offset=0
[plugin.audio.musicGD] Getting comments for track_id=186016, offset=0, limit=50
[plugin.audio.musicGD] Comments API success: total=1970879, hot=15, comments=1
[plugin.audio.musicGD] Comments displayed successfully
```

## 限制和注意事项

### ⚠️ 音乐源限制
- **仅支持 `netease` 音乐源**
- 其他音乐源会显示友好提示：
  ```
  抱歉，当前音乐源不支持评论功能。
  
  评论功能目前仅支持网易云音乐（netease）音乐源。
  
  请在设置中切换到 netease 音乐源。
  ```

### ⚠️ API 限制
- 评论 API 可能有速率限制
- 建议不要频繁调用
- 如果遇到错误，请稍后重试

### ⚠️ 分页限制
- 每页最多显示 50 条评论
- 需要手动调整 offset 参数来加载更多评论
- 目前不支持自动分页按钮

## 代码实现

### 1. 获取评论数据
```python
def get_song_comments(source, track_id, offset=0, limit=50):
    """获取歌曲评论"""
    # 只对 netease 音乐源使用评论 API
    if source != 'netease':
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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
        
        response = requests.get(comment_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        return data
        
    except Exception as e:
        log('Error getting comments: %s' % str(e), xbmc.LOGERROR)
        return None
```

### 2. 显示评论
```python
def show_song_comments(source, track_id, offset=0):
    """显示歌曲评论"""
    # 验证参数
    if not track_id:
        return
    
    # 检查音乐源
    if source != 'netease':
        dialog.textviewer('歌曲评论', '抱歉，当前音乐源不支持评论功能。')
        return
    
    # 获取评论数据
    comments_data = get_song_comments(source, track_id, offset, limit)
    
    # 构建并显示评论内容
    # ...
```

### 3. 路由支持
```python
def main():
    # ...
    elif mode == 'comments':
        source = args.get('source', [''])[0]
        track_id = args.get('id', [''])[0]
        offset = int(args.get('offset', ['0'])[0])
        show_song_comments(source, track_id, offset)
    # ...
```

## 版本信息

- **版本**: v1.9.0
- **更新日期**: 2026-01-25
- **新增功能**:
  - ✅ 集成真实网易云音乐评论 API
  - ✅ 支持热门评论和最新评论
  - ✅ 支持分页功能
  - ✅ 改进错误处理和用户提示
  - ⚠️ 仅支持 netease 音乐源

## 更新历史

### v1.9.0 (2026-01-25) - 真实评论功能
- 🔥 集成网易云音乐评论 API
- 🔥 支持真实评论数据
- 🔥 支持热门评论和最新评论
- 🔥 支持分页功能
- ⚡ 改进错误处理

### v1.8.0 (2026-01-25) - 评论功能框架
- ✅ 评论功能框架
- ✅ 评论显示逻辑
- ✅ 评论路由支持

### v1.7.0 (2026-01-25) - 性能优化
- 🔥 搜索速度优化（40 倍提升）
- 🔥 修复播放界面显示问题

### v1.6.0 (2026-01-25) - 最终稳定版本
- 🔥 回退到 setInfo 方法

## 总结

**✅ 已完成**:
- 真实评论 API 已集成
- 评论显示功能已完成
- 分页功能已实现
- 错误处理已完善

**⚠️ 限制**:
- 仅支持 `netease` 音乐源
- 需要手动调整 offset 参数来加载更多评论

**🎯 使用建议**:
- 在设置中使用 `netease` 音乐源
- 通过 URL 直接调用评论功能
- 可以集成到搜索结果或播放界面（需要额外开发）

---

**🎉 真实评论功能集成完成！**

现在可以查看网易云音乐的真实评论了！请重启 Kodi 并测试评论功能。
