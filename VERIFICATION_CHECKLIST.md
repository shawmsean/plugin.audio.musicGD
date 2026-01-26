# 验证清单：Arctic Fuse 3 皮肤评论按钮修复

## 📋 修改文件清单

### 1. 插件文件修改

**文件：** `plugin.audio.musicGD/main.py`

**修改内容：**
- ✅ 添加 `parse_xbmcswift2_url()` 函数
- ✅ 添加 `extract_song_id_from_play_url()` 函数
- ✅ 修改 `main()` 函数支持 xbmcswift2 路由

**验证方法：**
```bash
cd C:\Users\shawm\AppData\Roaming\Kodi\addons\plugin.audio.musicGD
python -m py_compile main.py
```

**预期结果：** 无错误输出

---

### 2. 皮肤文件修改

**文件：** `skin.arctic.fuse.3/1080i/MusicOSD.xml`

**修改位置：** 第 6010 号按钮（评论按钮），大约在第 155 行

**原始代码：**
```xml
<onclick>ActivateWindow(10025,plugin://plugin.audio.music/current_song_comments/0)</onclick>
```

**修复后代码：**
```xml
<!-- 动态识别当前播放的插件，并调用对应的评论路由 -->
<onclick condition="String.Contains(Player.Filenameandpath,plugin.audio.musicGD)">ActivateWindow(10025,plugin://plugin.audio.musicGD/current_song_comments/0)</onclick>
<onclick condition="!String.Contains(Player.Filenameandpath,plugin.audio.musicGD)">ActivateWindow(10025,plugin://plugin.audio.music/current_song_comments/0)</onclick>
```

**验证方法：**
打开文件 `MusicOSD.xml`，搜索 `current_song_comments`，确认修改已生效

**预期结果：** 找到两条 `<onclick>` 标签，分别对应 `plugin.audio.musicGD` 和 `plugin.audio.music`

---

## 🧪 功能测试清单

### 测试 1：路由解析测试

**测试文件：** `test_routing.py`

**测试命令：**
```bash
cd C:\Users\shawm\AppData\Roaming\Kodi\addons\plugin.audio.musicGD
python test_routing.py
```

**预期结果：**
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

**状态：** ✅ 已通过

---

### 测试 2：plugin.audio.musicGD 播放测试

**测试步骤：**
1. 启动 Kodi
2. 打开 `plugin.audio.musicGD`
3. 搜索并播放一首歌（例如：周杰伦 - 屋顶）
4. 播放歌曲
5. 打开 Arctic Fuse 3 皮肤的 MUSIC OSD
6. 点击"评论"按钮

**预期结果：**
- ✅ 成功显示评论对话框
- ✅ 显示当前播放歌曲的评论
- ✅ 包含热门评论和最新评论
- ✅ 显示分页信息

**日志验证：**
```
[plugin.audio.musicGD] Detected xbmcswift2 route: {'mode': 'current_song_comments', 'offset': '0'}
[plugin.audio.musicGD] Current play URL: plugin://plugin.audio.musicGD/?mode=play&source=netease&id=5257138&...
[plugin.audio.musicGD] Extracted from plugin.audio.musicGD: source=netease, track_id=5257138
[plugin.audio.musicGD] Getting comments for track_id=5257138, offset=0, limit=50
[plugin.audio.musicGD] Comments API success: total=1234, hot=10, comments=50
[plugin.audio.musicGD] Comments displayed successfully
```

**状态：** ⏳ 待用户测试

---

### 测试 3：plugin.audio.music 播放测试

**测试步骤：**
1. 启动 Kodi
2. 打开 `plugin.audio.music`
3. 搜索并播放一首歌
4. 播放歌曲
5. 打开 Arctic Fuse 3 皮肤的 MUSIC OSD
6. 点击"评论"按钮

**预期结果：**
- ✅ 成功显示评论对话框
- ✅ 显示当前播放歌曲的评论
- ✅ 包含热门评论和最新评论
- ✅ 显示分页信息

**日志验证：**
```
[xbmcswift2] Request for "/current_song_comments/0" matches rule for function "current_song_comments"
[Music Comments] Current play URL: plugin://plugin.audio.music/play/song/1811921555/0/0/207/netease/
[Music Comments] Extracted song_id: 1811921555
[Music Comments] Getting comments for track_id=1811921555, offset=0, limit=50
[Music Comments] Comments API success: total=567, hot=5, comments=50
```

**状态：** ⏳ 待用户测试

---

### 测试 4：跨插件兼容性测试

**测试步骤：**
1. 使用 `plugin.audio.musicGD` 播放歌曲 A
2. 点击"评论"按钮，确认显示歌曲 A 的评论
3. 关闭评论对话框
4. 切换到 `plugin.audio.music` 播放歌曲 B
5. 点击"评论"按钮，确认显示歌曲 B 的评论

**预期结果：**
- ✅ 第一次点击显示歌曲 A 的评论
- ✅ 第二次点击显示歌曲 B 的评论
- ✅ 两个插件的评论功能都能正常工作

**状态：** ⏳ 待用户测试

---

### 测试 5：错误处理测试

**测试场景 5.1：未播放音乐时点击评论按钮**

**测试步骤：**
1. 确保没有正在播放的音乐
2. 打开 Arctic Fuse 3 皮肤的 MUSIC OSD
3. 点击"评论"按钮

**预期结果：**
- ✅ 显示错误通知："无法从播放URL提取歌曲ID"
- ✅ Kodi 日志中记录错误信息

**状态：** ⏳ 待用户测试

---

**测试场景 5.2：播放不支持的音乐源**

**测试步骤：**
1. 使用 `plugin.audio.musicGD` 播放非 netease 音乐源的歌曲（如果支持）
2. 点击"评论"按钮

**预期结果：**
- ✅ 显示提示："当前音乐源不支持评论功能"
- ✅ 说明评论功能仅支持 netease 音乐源

**状态：** ⏳ 待用户测试

---

## 📊 测试结果汇总

| 测试项 | 状态 | 备注 |
|--------|------|------|
| 路由解析测试 | ✅ 通过 | 所有 7 个测试用例通过 |
| plugin.audio.musicGD 播放测试 | ⏳ 待测试 | 需要用户在 Kodi 中测试 |
| plugin.audio.music 播放测试 | ⏳ 待测试 | 需要用户在 Kodi 中测试 |
| 跨插件兼容性测试 | ⏳ 待测试 | 需要用户在 Kodi 中测试 |
| 错误处理测试 | ⏳ 待测试 | 需要用户在 Kodi 中测试 |

---

## 🔍 调试信息收集

如果测试失败，请收集以下信息：

### 1. Kodi 日志

**日志位置：**
- Windows: `C:\Users\[用户名]\AppData\Roaming\Kodi\kodi.log`

**需要查找的关键信息：**
```
[plugin.audio.musicGD] Detected xbmcswift2 route
[plugin.audio.musicGD] Current play URL
[plugin.audio.musicGD] Extracted from
[plugin.audio.musicGD] Getting comments for track_id
[plugin.audio.musicGD] Comments API success
```

### 2. 播放 URL

**获取方法：**
1. 播放一首歌
2. 在 Kodi 中按 `Ctrl+Shift+O` 打开调试信息
3. 查看 `Player.Filenameandpath` 的值

**预期格式：**
```
plugin://plugin.audio.musicGD/?mode=play&source=netease&id=5257138&pic_id=109951165671182684&lyric_id=5257138&name=屋顶&artist=周杰伦&album=Jay
```

### 3. 皮肤调用 URL

**获取方法：**
1. 打开 `MusicOSD.xml` 文件
2. 查找第 6010 号按钮的 `<onclick>` 标签
3. 确认调用的 URL

**预期格式：**
```xml
<onclick condition="String.Contains(Player.Filenameandpath,plugin.audio.musicGD)">ActivateWindow(10025,plugin://plugin.audio.musicGD/current_song_comments/0)</onclick>
<onclick condition="!String.Contains(Player.Filenameandpath,plugin.audio.musicGD)">ActivateWindow(10025,plugin://plugin.audio.music/current_song_comments/0)</onclick>
```

---

## ✅ 完成标准

当以下所有条件都满足时，说明修复成功：

1. ✅ `main.py` 语法检查通过
2. ✅ `test_routing.py` 所有测试通过
3. ✅ `MusicOSD.xml` 文件已正确修改
4. ✅ 使用 `plugin.audio.musicGD` 播放歌曲
5. ✅ 点击"评论"按钮成功显示评论
6. ✅ 使用 `plugin.audio.music` 播放歌曲
7. ✅ 点击"评论"按钮成功显示评论
8. ✅ 两个插件的评论功能都能正常工作
9. ✅ 错误处理正常工作

---

## 📝 测试报告模板

请使用以下模板记录测试结果：

```
测试日期：____-__-__
测试人员：__________
Kodi 版本：__________
皮肤版本：Arctic Fuse 3

测试结果：
- [ ] 路由解析测试通过
- [ ] plugin.audio.musicGD 播放测试通过
- [ ] plugin.audio.music 播放测试通过
- [ ] 跨插件兼容性测试通过
- [ ] 错误处理测试通过

遇到的问题：
1. _________________
2. _________________
3. _________________

其他备注：
_______________
```

---

## 📞 获取帮助

如果遇到问题，请：

1. 查看 Kodi 日志获取详细错误信息
2. 运行 `test_routing.py` 验证路由解析
3. 检查皮肤文件是否正确修改
4. 查看 `SOLUTION_SUMMARY.md` 了解完整解决方案
5. 查看 `SKIN_FIX.md` 了解皮肤修复详情

---

**最后更新：** 2026-01-26
**版本：** 1.0.0
**状态：** ✅ 代码已完成，等待用户测试验证
