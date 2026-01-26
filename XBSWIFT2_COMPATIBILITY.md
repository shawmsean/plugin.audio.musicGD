# xbmcswift2 路由兼容性实现

## 问题背景

`skin.arctic.fuse.3` 皮肤的 MUSIC OSD 中的"歌曲评论"按钮会调用 xbmcswift2 框架的路由：
- `/current_song_comments/<offset>`

这个路由最初是为 `plugin.audio.music` 插件设计的，该插件使用 xbmcswift2 框架。

`plugin.audio.musicGD` 插件使用原生 Kodi 路由机制（`parse_qs` 解析 URL 参数），两者不兼容。

## 解决方案

在不修改 `plugin.audio.music` 插件的情况下，为 `plugin.audio.musicGD` 添加 xbmcswift2 路由兼容层。

## 实现细节

### 1. xbmcswift2 URL 解析

添加 `parse_xbmcswift2_url()` 函数，解析 xbmcswift2 风格的 URL 路径：

```python
def parse_xbmcswift2_url(path):
    """
    解析 xbmcswift2 风格的 URL 路径

    支持的路由:
    - /current_song_comments/<offset>
    - /song_comments/<song_id>/<offset>

    返回:
        dict: 解析后的参数
    """
```

**支持的 URL 格式：**
- `/current_song_comments/0` → `{'mode': 'current_song_comments', 'offset': '0'}`
- `/current_song_comments/50` → `{'mode': 'current_song_comments', 'offset': '50'}`
- `/song_comments/123456/0` → `{'mode': 'comments', 'id': '123456', 'offset': '0', 'source': 'netease'}`

### 2. 从播放 URL 提取歌曲 ID

添加 `extract_song_id_from_play_url()` 函数，从当前播放的 URL 中提取歌曲 ID：

```python
def extract_song_id_from_play_url():
    """
    从当前播放的 URL 中提取歌曲 ID

    支持的播放 URL 格式:
    - plugin://plugin.audio.musicGD/?mode=play&source=netease&id=12345&...
    - plugin://plugin.audio.music/play/song/1811921555/0/0/207/netease/

    返回:
        tuple: (source, track_id) 或 (None, None)
    """
```

**支持的播放 URL：**
1. **plugin.audio.musicGD 格式：**
   ```
   plugin://plugin.audio.musicGD/?mode=play&source=netease&id=5257138&pic_id=109951165671182684&lyric_id=5257138&name=屋顶&artist=周杰伦&album=Jay
   ```
   提取结果：`source='netease'`, `track_id='5257138'`

2. **plugin.audio.music 格式：**
   ```
   plugin://plugin.audio.music/play/song/1811921555/0/0/207/netease/
   ```
   提取结果：`source='netease'`, `track_id='1811921555'`

### 3. 修改 main() 函数

在 `main()` 函数中添加 xbmcswift2 路由处理逻辑：

```python
def main():
    """Main plugin entry point"""

    # 首先尝试解析 xbmcswift2 风格的 URL 路径
    if len(sys.argv) > 0 and sys.argv[0]:
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
                        # 显示错误提示
                        dialog = xbmcgui.Dialog()
                        dialog.notification('错误', '无法从播放URL提取歌曲ID')
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

    # 原有的参数解析逻辑（向后兼容）
    args = parse_qs(sys.argv[2][1:]) if len(sys.argv) > 2 else {}
    mode = args.get('mode', [''])[0]

    # ... 原有逻辑 ...
```

## 工作流程

### 场景：用户在 Arctic Fuse 3 皮肤中点击评论按钮

1. **皮肤触发：**
   ```
   plugin://plugin.audio.musicGD/current_song_comments/0
   ```

2. **插件解析：**
   - `sys.argv[0]` = `plugin://plugin.audio.musicGD/current_song_comments/0`
   - 解析路径：`path = '/current_song_comments/0'`
   - 调用 `parse_xbmcswift2_url('/current_song_comments/0')`
   - 返回：`{'mode': 'current_song_comments', 'offset': '0'}`

3. **提取歌曲 ID：**
   - 调用 `extract_song_id_from_play_url()`
   - 获取当前播放 URL：
     ```
     plugin://plugin.audio.musicGD/?mode=play&source=netease&id=5257138&pic_id=109951165671182684&lyric_id=5257138&name=屋顶&artist=周杰伦&album=Jay
     ```
   - 解析参数：`source='netease'`, `track_id='5257138'`

4. **显示评论：**
   - 调用 `show_song_comments('netease', '5257138', 0)`
   - 从 API 获取评论数据
   - 在对话框中显示评论

## 兼容性

### 支持的路由

| 路由格式 | 说明 | 兼容插件 |
|---------|------|---------|
| `/?mode=play&source=xxx&id=xxx` | 原生路由 | plugin.audio.musicGD |
| `/?mode=comments&source=xxx&id=xxx` | 原生路由 | plugin.audio.musicGD |
| `/current_song_comments/<offset>` | xbmcswift2 路由 | plugin.audio.music, plugin.audio.musicGD |
| `/song_comments/<song_id>/<offset>` | xbmcswift2 路由 | plugin.audio.music, plugin.audio.musicGD |

### 支持的播放 URL

| 播放 URL 格式 | 来源 | 提取结果 |
|--------------|------|---------|
| `plugin://plugin.audio.musicGD/?mode=play&...` | plugin.audio.musicGD | ✅ 提取成功 |
| `plugin://plugin.audio.music/play/song/...` | plugin.audio.music | ✅ 提取成功 |
| 其他格式 | - | ❌ 提取失败 |

## 测试

运行路由解析测试：

```bash
python test_routing.py
```

测试结果：
```
[PASS] URL: /current_song_comments/0
[PASS] URL: /current_song_comments/50
[PASS] URL: /current_song_comments/
[PASS] URL: /song_comments/123456/0
[PASS] URL: /song_comments/123456/50
[PASS] URL: /
[PASS] URL:

All tests PASSED!
```

## 使用说明

### 对于用户

1. 使用 `plugin.audio.musicGD` 播放音乐
2. 在 Arctic Fuse 3 皮肤的 MUSIC OSD 中点击"评论"按钮
3. 插件会自动识别当前播放的歌曲并显示评论

### 对于开发者

如果需要添加更多 xbmcswift2 路由支持，按照以下步骤：

1. 在 `parse_xbmcswift2_url()` 中添加新的路由识别逻辑
2. 在 `main()` 函数中添加对应的处理逻辑
3. 运行 `test_routing.py` 验证路由解析

## 优势

✅ **完全兼容**：支持 xbmcswift2 和原生 Kodi 路由
✅ **无需修改**：不需要修改 `plugin.audio.music` 插件
✅ **向后兼容**：保留原有的原生路由逻辑
✅ **跨插件支持**：可以识别 `plugin.audio.music` 的播放 URL
✅ **易于扩展**：可以轻松添加更多 xbmcswift2 路由支持

## 注意事项

1. **歌曲 ID 提取依赖播放 URL**：如果播放 URL 格式不符合预期，将无法提取歌曲 ID
2. **仅支持 netease 音乐源的评论**：评论 API 目前只支持网易云音乐
3. **需要歌曲正在播放**：`/current_song_comments/0` 路由需要歌曲正在播放才能提取 ID

## 故障排除

### 问题：点击评论按钮提示"无法从播放URL提取歌曲ID"

**原因：** 当前没有播放音乐，或者播放 URL 格式不支持

**解决方案：**
- 确保正在播放 `plugin.audio.musicGD` 或 `plugin.audio.music` 的歌曲
- 查看日志中的 "Current play URL" 信息
- 确认播放 URL 格式是否在支持列表中

### 问题：评论显示"当前音乐源不支持评论功能"

**原因：** 评论功能目前只支持 netease 音乐源

**解决方案：**
- 确保播放的歌曲来自 netease 音乐源
- 在插件设置中将默认音乐源设置为 netease

## 版本历史

- **v1.0.0** (2026-01-26): 初始实现，支持 xbmcswift2 路由兼容
