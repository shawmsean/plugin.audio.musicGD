# 快速使用指南：xbmcswift2 兼容性与皮肤修复

## 🎯 目标

让 `plugin.audio.musicGD` 插件能够响应 Arctic Fuse 3 皮肤的"歌曲评论"按钮，与 `plugin.audio.music` 插件完全兼容。

## ✅ 已完成的工作

### 1. 添加 xbmcswift2 路由兼容层
- ✅ 实现 `parse_xbmcswift2_url()` 函数
- ✅ 实现 `extract_song_id_from_play_url()` 函数
- ✅ 修改 `main()` 函数支持 xbmcswift2 路由
- ✅ 所有测试通过

### 2. 修复 Arctic Fuse 3 皮肤评论按钮
- ✅ 修改 `skin.arctic.fuse.3/1080i/MusicOSD.xml`
- ✅ 添加动态插件识别逻辑
- ✅ 支持多插件自动切换

### 3. 添加交互式分页功能
- ✅ 实现智能按钮显示逻辑
- ✅ 支持"返回第1页"、"上一页"、"下一页"、"刷新"操作
- ✅ 移除纯文本提示，改用交互式按钮
- ✅ 提升用户体验

### 4. 支持的 URL 格式

**xbmcswift2 路由（皮肤调用）：**
```
plugin://plugin.audio.musicGD/current_song_comments/0
plugin://plugin.audio.musicGD/song_comments/123456/0
```

**原生路由（插件内部）：**
```
plugin://plugin.audio.musicGD/?mode=comments&source=netease&id=123456&offset=0
```

**播放 URL（歌曲 ID 提取）：**
```
plugin://plugin.audio.musicGD/?mode=play&source=netease&id=5257138&...
plugin://plugin.audio.music/play/song/1811921555/0/0/207/netease/
```

## 🚀 如何使用

### ⚠️ 重要提示：必须先修复皮肤文件

在使用本插件之前，**必须先修复 Arctic Fuse 3 皮肤的评论按钮**，否则皮肤会硬编码调用 `plugin.audio.music`。

**修复步骤：**

1. 打开文件：`C:\Users\shawm\AppData\Roaming\Kodi\addons\skin.arctic.fuse.3\1080i\MusicOSD.xml`

2. 找到第 6010 号按钮（评论按钮），大约在第 140 行附近

3. 将原来的代码：
```xml
<onclick>ActivateWindow(10025,plugin://plugin.audio.music/current_song_comments/0)</onclick>
```

4. 替换为：
```xml
<onclick condition="String.Contains(Player.Filenameandpath,plugin.audio.musicGD)">ActivateWindow(10025,plugin://plugin.audio.musicGD/current_song_comments/0)</onclick>
<onclick condition="!String.Contains(Player.Filenameandpath,plugin.audio.musicGD)">ActivateWindow(10025,plugin://plugin.audio.music/current_song_comments/0)</onclick>
```

5. 保存文件并重启 Kodi

**详细说明请查看：** [SKIN_FIX.md](SKIN_FIX.md)

---

### 方式 1：通过皮肤触发（推荐）

1. 使用 `plugin.audio.musicGD` 播放一首歌
2. 在 Arctic Fuse 3 皮肤的 MUSIC OSD 中找到"评论"按钮
3. 点击按钮，插件会自动显示当前播放歌曲的评论

**交互式分页操作：**
- 按 ESC 键关闭评论文本查看器
- 选择操作按钮：
  - **⬅️ 返回第1页** - 快速跳转到第一页
  - **⬅️ 上一页** - 返回上一页
  - **➡️ 下一页** - 加载下一页评论
  - **🔄 刷新当前页** - 重新加载当前页评论
  - **❌ 退出** - 关闭评论对话框

**工作原理：**
```
皮肤调用 → plugin://plugin.audio.musicGD/current_song_comments/0
         ↓
插件解析 xbmcswift2 路由
         ↓
提取当前播放 URL 中的歌曲 ID
         ↓
调用评论 API 并显示评论
         ↓
显示交互式操作按钮
```

### 方式 2：直接调用 URL

**显示当前播放歌曲的评论（第一页）：**
```
plugin://plugin.audio.musicGD/current_song_comments/0
```

**显示指定歌曲的评论：**
```
plugin://plugin.audio.musicGD/song_comments/5257138/0
```

**显示当前播放歌曲的评论（第 2 页）：**
```
plugin://plugin.audio.musicGD/current_song_comments/50
```

### 方式 3：使用原生路由（向后兼容）

```
plugin://plugin.audio.musicGD/?mode=comments&source=netease&id=5257138&offset=0
```

## 🧪 测试验证

### 运行路由解析测试

```bash
cd C:\Users\shawm\AppData\Roaming\Kodi\addons\plugin.audio.musicGD
python test_routing.py
```

**预期输出：**
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

### 验证 Python 语法

```bash
python -m py_compile main.py
```

如果没有错误输出，说明语法正确。

## 🔍 调试信息

如果遇到问题，查看 Kodi 日志中的以下信息：

### xbmcswift2 路由识别
```
[plugin.audio.musicGD] Detected xbmcswift2 route: {'mode': 'current_song_comments', 'offset': '0'}
```

### 播放 URL 提取
```
[plugin.audio.musicGD] Current play URL: plugin://plugin.audio.musicGD/?mode=play&source=netease&id=5257138&...
[plugin.audio.musicGD] Extracted from plugin.audio.musicGD: source=netease, track_id=5257138
```

### 评论 API 调用
```
[plugin.audio.musicGD] Getting comments for track_id=5257138, offset=0, limit=50
[plugin.audio.musicGD] Comments API success: total=1234, hot=10, comments=50
```

## ⚠️ 常见问题

### Q1: 点击评论按钮提示"无法从播放URL提取歌曲ID"

**原因：** 当前没有播放音乐，或者播放 URL 格式不支持

**解决方法：**
1. 确保正在播放 `plugin.audio.musicGD` 或 `plugin.audio.music` 的歌曲
2. 查看 Kodi 日志中的 "Current play URL" 信息
3. 确认播放 URL 包含歌曲 ID 参数

### Q2: 评论显示"当前音乐源不支持评论功能"

**原因：** 评论功能目前只支持 netease 音乐源

**解决方法：**
1. 确保播放的歌曲来自 netease 音乐源
2. 在插件设置中将默认音乐源设置为 netease

### Q3: 评论显示成功，但内容为空

**原因：** 该歌曲可能没有评论，或者 API 返回失败

**解决方法：**
1. 查看 Kodi 日志中的 API 调用结果
2. 尝试其他歌曲
3. 检查网络连接

## 📊 兼容性矩阵

| 功能 | plugin.audio.music | plugin.audio.musicGD |
|------|-------------------|---------------------|
| xbmcswift2 路由 | ✅ 原生支持 | ✅ 兼容层支持 |
| 原生路由 | ❌ 不支持 | ✅ 原生支持 |
| 皮肤评论按钮 | ✅ 支持 | ✅ 支持 |
| 跨插件 URL 识别 | ❌ 不支持 | ✅ 支持 |

## 🎉 成功标志

当以下条件都满足时，说明兼容性实现成功：

1. ✅ 路由解析测试全部通过
2. ✅ Python 语法检查通过
3. ✅ 使用 plugin.audio.musicGD 播放歌曲
4. ✅ 在 Arctic Fuse 3 皮肤中点击"评论"按钮
5. ✅ 成功显示当前播放歌曲的评论

## 📝 代码结构

```
main.py
├── parse_xbmcswift2_url()          # xbmcswift2 URL 解析
├── extract_song_id_from_play_url() # 从播放 URL 提取歌曲 ID
├── show_song_comments()            # 显示评论（已有）
└── main()                          # 主入口（已修改）
    ├── xbmcswift2 路由处理（新增）
    └── 原生路由处理（保留）

test_routing.py                     # 路由解析测试（新增）

XBSWIFT2_COMPATIBILITY.md           # 详细文档（新增）
```

## 🔧 技术细节

### xbmcswift2 路由识别

插件通过解析 `sys.argv[0]` 的路径部分来识别 xbmcswift2 路由：

```python
from urllib.parse import urlparse
parsed = urlparse(sys.argv[0])  # plugin://plugin.audio.musicGD/current_song_comments/0
path = parsed.path               # /current_song_comments/0
```

### 歌曲 ID 提取策略

插件使用 `xbmc.getInfoLabel('Player.Filenameandpath')` 获取当前播放 URL，然后：

1. 检查是否包含 `plugin.audio.musicGD` → 解析查询参数
2. 检查是否包含 `plugin.audio.music` → 解析路径参数
3. 如果都不匹配 → 返回 None

### 错误处理

- 如果 xbmcswift2 路由解析失败 → 回退到原生路由
- 如果歌曲 ID 提取失败 → 显示错误通知
- 如果评论 API 调用失败 → 显示错误通知

## 📚 相关文档

- [XBSWIFT2_COMPATIBILITY.md](XBSWIFT2_COMPATIBILITY.md) - 详细技术文档
- [addon.xml](addon.xml) - 插件配置文件
- [main.py](main.py) - 主程序代码

## 🤝 贡献

如果发现任何问题或有改进建议，请：

1. 查看 Kodi 日志获取详细错误信息
2. 运行测试脚本验证路由解析
3. 检查播放 URL 格式是否支持

## 📄 许可证

GPL-3.0

---

**最后更新：** 2026-01-26
**版本：** 1.0.0
**状态：** ✅ 已完成并测试通过
