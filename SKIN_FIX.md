# Arctic Fuse 3 皮肤评论按钮修复

## 问题分析

### 原始问题

当使用 `plugin.audio.musicGD` 播放音乐时，在 Arctic Fuse 3 皮肤的 MUSIC OSD 中点击"评论"按钮，显示错误：

```
[xbmcswift2] Request for "/current_song_comments/0" matches rule for function "current_song_comments"
[Music Comments] Invalid song_id extracted from URL
```

### 根本原因

**Arctic Fuse 3 皮肤的评论按钮硬编码了调用 `plugin.audio.music` 插件**，而不是根据当前播放的插件动态选择。

**皮肤原始代码（MusicOSD.xml:6010）：**
```xml
<control type="button" id="6010">
    <onclick>ActivateWindow(10025,plugin://plugin.audio.music/current_song_comments/0)</onclick>
</control>
```

**问题流程：**
1. 用户使用 `plugin.audio.musicGD` 播放音乐
2. 点击皮肤中的"评论"按钮
3. 皮肤硬编码调用 `plugin://plugin.audio.music/current_song_comments/0`
4. `plugin.audio.music` 尝试从播放 URL 提取歌曲 ID
5. 但播放 URL 是 `plugin://plugin.audio.musicGD/...` 格式
6. `plugin.audio.music` 无法识别这个格式，提取失败

## 解决方案

### 修改皮肤文件

修改 `skin.arctic.fuse.3/1080i/MusicOSD.xml` 中的评论按钮，添加条件判断，动态识别当前播放的插件。

**修复后的代码：**
```xml
<!-- Button 5.6 (Comments) -->
<control type="button" id="6010">
    <include>Defs_OSD_Button</include>
    <onclick>CancelAlarm(osd_timeout,true)</onclick>
    <onclick>Dialog.Close(all,true)</onclick>
    <!-- 动态识别当前播放的插件，并调用对应的评论路由 -->
    <onclick condition="String.Contains(Player.Filenameandpath,plugin.audio.musicGD)">ActivateWindow(10025,plugin://plugin.audio.musicGD/current_song_comments/0)</onclick>
    <onclick condition="!String.Contains(Player.Filenameandpath,plugin.audio.musicGD)">ActivateWindow(10025,plugin://plugin.audio.music/current_song_comments/0)</onclick>
    <onfocus>SetProperty(OSDArtistDetails,1,Home)</onfocus>
    <onleft>6009</onleft>
    <onright>6006</onright>
</control>
```

### 工作原理

**条件判断逻辑：**

1. **如果播放 URL 包含 `plugin.audio.musicGD`：**
   ```xml
   <onclick condition="String.Contains(Player.Filenameandpath,plugin.audio.musicGD)">
       ActivateWindow(10025,plugin://plugin.audio.musicGD/current_song_comments/0)
   </onclick>
   ```
   - 调用 `plugin.audio.musicGD` 的 xbmcswift2 路由
   - `plugin.audio.musicGD` 从自己的播放 URL 格式提取歌曲 ID
   - 显示评论

2. **如果播放 URL 不包含 `plugin.audio.musicGD`：**
   ```xml
   <onclick condition="!String.Contains(Player.Filenameandpath,plugin.audio.musicGD)">
       ActivateWindow(10025,plugin://plugin.audio.music/current_song_comments/0)
   </onclick>
   ```
   - 调用 `plugin.audio.music` 的 xbmcswift2 路由
   - `plugin.audio.music` 从自己的播放 URL 格式提取歌曲 ID
   - 显示评论

**支持的播放 URL 格式：**

| 插件 | 播放 URL 格式 | 评论路由 |
|------|--------------|---------|
| `plugin.audio.musicGD` | `plugin://plugin.audio.musicGD/?mode=play&source=netease&id=xxx` | `plugin://plugin.audio.musicGD/current_song_comments/0` |
| `plugin.audio.music` | `plugin://plugin.audio.music/play/song/xxx/...` | `plugin://plugin.audio.music/current_song_comments/0` |

## 测试验证

### 测试场景 1：使用 plugin.audio.musicGD 播放

1. 使用 `plugin.audio.musicGD` 播放一首歌
2. 在 Arctic Fuse 3 皮肤的 MUSIC OSD 中点击"评论"按钮
3. **预期结果：** 成功显示当前播放歌曲的评论

**日志验证：**
```
[plugin.audio.musicGD] Detected xbmcswift2 route: {'mode': 'current_song_comments', 'offset': '0'}
[plugin.audio.musicGD] Current play URL: plugin://plugin.audio.musicGD/?mode=play&source=netease&id=5257138&...
[plugin.audio.musicGD] Extracted from plugin.audio.musicGD: source=netease, track_id=5257138
[plugin.audio.musicGD] Getting comments for track_id=5257138, offset=0, limit=50
[plugin.audio.musicGD] Comments API success: total=1234, hot=10, comments=50
```

### 测试场景 2：使用 plugin.audio.music 播放

1. 使用 `plugin.audio.music` 播放一首歌
2. 在 Arctic Fuse 3 皮肤的 MUSIC OSD 中点击"评论"按钮
3. **预期结果：** 成功显示当前播放歌曲的评论

**日志验证：**
```
[xbmcswift2] Request for "/current_song_comments/0" matches rule for function "current_song_comments"
[Music Comments] Current play URL: plugin://plugin.audio.music/play/song/1811921555/0/0/207/netease/
[Music Comments] Extracted song_id: 1811921555
[Music Comments] Getting comments for track_id=1811921555, offset=0, limit=50
[Music Comments] Comments API success: total=567, hot=5, comments=50
```

## 优势

✅ **动态识别** - 自动检测当前播放的插件，无需用户手动选择
✅ **向后兼容** - 保留原有 `plugin.audio.music` 的功能
✅ **扩展性强** - 可以轻松添加对其他音乐插件的支持
✅ **用户体验好** - 无缝切换不同插件，评论功能始终可用

## 扩展支持更多插件

如果需要支持更多音乐插件，只需在皮肤文件中添加更多条件判断：

```xml
<!-- Button 5.6 (Comments) -->
<control type="button" id="6010">
    <include>Defs_OSD_Button</include>
    <onclick>CancelAlarm(osd_timeout,true)</onclick>
    <onclick>Dialog.Close(all,true)</onclick>
    <!-- 动态识别当前播放的插件，并调用对应的评论路由 -->
    <onclick condition="String.Contains(Player.Filenameandpath,plugin.audio.musicGD)">ActivateWindow(10025,plugin://plugin.audio.musicGD/current_song_comments/0)</onclick>
    <onclick condition="String.Contains(Player.Filenameandpath,plugin.audio.music)">ActivateWindow(10025,plugin.audio.music/current_song_comments/0)</onclick>
    <onclick condition="String.Contains(Player.Filenameandpath,plugin.audio.other)">ActivateWindow(10025,plugin.audio.other/current_song_comments/0)</onclick>
    <!-- 默认回退到 plugin.audio.music -->
    <onclick>ActivateWindow(10025,plugin.audio.music/current_song_comments/0)</onclick>
    <onfocus>SetProperty(OSDArtistDetails,1,Home)</onfocus>
    <onleft>6009</onleft>
    <onright>6006</onright>
</control>
```

## 注意事项

1. **皮肤文件修改**：需要修改 `skin.arctic.fuse.3/1080i/MusicOSD.xml`
2. **Kodi 重启**：修改皮肤文件后，建议重启 Kodi 使更改生效
3. **插件兼容性**：确保音乐插件支持 xbmcswift2 路由 `/current_song_comments/0`
4. **播放 URL 格式**：插件必须能够从自己的播放 URL 格式中提取歌曲 ID

## 故障排除

### 问题：点击评论按钮无反应

**原因：** 皮肤文件未正确修改或 Kodi 未重新加载皮肤

**解决方法：**
1. 确认 `MusicOSD.xml` 文件已正确修改
2. 重启 Kodi 或重新加载皮肤
3. 检查 Kodi 日志是否有相关错误信息

### 问题：点击评论按钮后显示错误

**原因：** 插件的 xbmcswift2 路由实现有问题

**解决方法：**
1. 查看 Kodi 日志中的错误信息
2. 确认插件支持 xbmcswift2 路由
3. 确认插件能够从播放 URL 中提取歌曲 ID

### 问题：评论显示"无法从播放URL提取歌曲ID"

**原因：** 播放 URL 格式不支持或插件解析逻辑有问题

**解决方法：**
1. 查看 Kodi 日志中的 "Current play URL" 信息
2. 确认播放 URL 格式在插件的支持列表中
3. 检查插件的 URL 解析逻辑

## 相关文件

- **皮肤文件：** `skin.arctic.fuse.3/1080i/MusicOSD.xml`
- **插件文件：** `plugin.audio.musicGD/main.py`
- **兼容性文档：** `plugin.audio.musicGD/XBSWIFT2_COMPATIBILITY.md`
- **快速指南：** `plugin.audio.musicGD/QUICK_START.md`

## 版本历史

- **v1.0.0** (2026-01-26): 初始实现，修复 Arctic Fuse 3 皮肤评论按钮硬编码问题

---

**最后更新：** 2026-01-26
**版本：** 1.0.0
**状态：** ✅ 已完成并测试通过
