# plugin.audio.musicGD

GD 音乐台 Kodi 音乐插件 - 基于 GD 音乐台 API 的音乐搜索、播放和歌单浏览插件。

## 📋 功能特性

### 核心功能
- ✅ **音乐搜索** - 支持多音乐源搜索（网易云音乐、酷我音乐等）
- ✅ **歌曲播放** - 支持多种音质（128/192/320/无损）
- ✅ **专辑封面** - 自动获取和显示专辑封面
- ✅ **歌词显示** - 支持歌词缓存和显示
- ✅ **歌单浏览** - 高质量歌单浏览和播放
- ✅ **评论功能** - 查看歌曲评论，支持分页
- ✅ **批量播放** - 支持播放歌单中的所有歌曲

### 高级功能
- ✅ **xbmcswift2 兼容** - 兼容 xbmcswift2 路由框架
- ✅ **皮肤集成** - 支持 Arctic Fuse 3 皮肤
- ✅ **交互式分页** - 交互式分页导航
- ✅ **速率限制** - 智能速率限制和重试机制
- ✅ **缓存机制** - 专辑封面和歌词缓存
- ✅ **SSL/TLS 支持** - 安全的 HTTPS 连接

## 🚀 安装方法

### 方法 1：从 Zip 文件安装

1. 下载最新版本的 zip 文件
2. 在 Kodi 中打开"设置" → "插件" → "从 ZIP 文件安装"
3. 选择下载的 zip 文件
4. 等待安装完成

### 方法 2：从源码安装

1. 克隆或下载此仓库
2. 将 `plugin.audio.musicGD` 文件夹复制到 Kodi 的 addons 目录：
   - Windows: `%APPDATA%\Kodi\addons\`
   - Linux: `~/.kodi/addons/`
   - macOS: `~/Library/Application Support/Kodi/addons/`
3. 重启 Kodi

## 📖 使用指南

### 基本使用

1. **搜索音乐**
   - 打开插件，选择"搜索音乐"
   - 输入歌曲名、歌手名或专辑名
   - 浏览搜索结果
   - 选择歌曲播放

2. **浏览歌单**
   - 选择"歌单精选"
   - 选择分类（华语、流行、摇滚等）
   - 浏览高质量歌单
   - 选择歌单查看歌曲列表
   - 点击"播放全部"或选择单首歌曲

3. **查看评论**
   - 在 Arctic Fuse 3 皮肤中播放歌曲
   - 在 MUSIC OSD 中点击"评论"按钮
   - 使用交互式分页浏览评论

### 高级功能

- **音质设置** - 在插件设置中选择默认音质
- **缓存管理** - 启用/禁用专辑封面和歌词缓存
- **评论分页** - 使用交互式按钮浏览多页评论

## 🔧 技术细节

### API 端点

| 功能 | API 端点 |
|------|---------|
| 搜索 | `https://music-api.gdstudio.xyz/api.php?types=search` |
| 播放 URL | `https://music-api.gdstudio.xyz/api.php?types=url` |
| 专辑封面 | `https://music-api.gdstudio.xyz/api.php?types=pic` |
| 歌词 | `https://music-api.gdstudio.xyz/api.php?types=lyric` |
| 歌单标签 | `https://apis.netstart.cn/music/playlist/highquality/tags` |
| 高质量歌单 | `https://apis.netstart.cn/music/top/playlist/highquality` |
| 歌单详情 | `https://apis.netstart.cn/music/playlist/detail` |

### 支持的音乐源

- ✅ netease（网易云音乐）- 推荐
- ✅ kuwo（酷我音乐）
- ✅ joox
- ⚠️ 其他音乐源可能不稳定

### 技术栈

- **语言**: Python 3
- **框架**: Kodi Plugin
- **网络**: requests
- **加密**: ssl

## 📝 配置说明

### 插件设置

在 Kodi 插件设置中可以配置：

- **默认音乐源** - 选择默认使用的音乐源
- **默认音质** - 选择播放音质（128/192/320/无损）
- **缓存启用** - 启用/禁用专辑封面和歌词缓存

### 速率限制

- **限制**: 5 分钟内不超过 50 次请求
- **实现**: 全局请求队列 + 令牌桶限流
- **重试**: 指数退避重试机制

## 🐛 故障排除

### 常见问题

**1. 搜索无结果**
- 检查网络连接
- 尝试不同的音乐源
- 检查搜索关键字是否正确

**2. 播放失败**
- 检查歌曲是否已下架
- 尝试降低音质
- 检查 API 是否可用

**3. 评论功能不工作**
- 确保使用 netease 音乐源
- 检查皮肤是否已修复
- 查看 Kodi 日志获取详细信息

### 调试信息

查看 Kodi 日志获取详细错误信息：
- Windows: `%APPDATA%\Kodi\kodi.log`
- Linux: `~/.kodi/temp/kodi.log`
- macOS: `~/Library/Application Support/Kodi/logs/kodi.log`

## 📚 文档

- [QUICK_START.md](QUICK_START.md) - 快速开始指南
- [PLAYLIST_FEATURE.md](PLAYLIST_FEATURE.md) - 歌单功能说明
- [XBSWIFT2_COMPATIBILITY.md](XBSWIFT2_COMPATIBILITY.md) - xbmcswift2 兼容性
- [SKIN_FIX.md](SKIN_FIX.md) - 皮肤修复说明
- [INTERACTIVE_PAGINATION.md](INTERACTIVE_PAGINATION.md) - 交互式分页功能

## 🤝 贡献

欢迎提交问题和改进建议！

## 📄 许可证

GPL-3.0

## 🙏 致谢

- **GD 音乐台** - 提供 API 服务 [music.gdstudio.xyz](https://music.gdstudio.xyz)
- **Kodi 社区** - 提供插件开发框架
- **网易云音乐** - 提供音乐数据

## 📢 免责声明

本插件仅供个人学习和研究使用。请遵守相关法律法规和版权规定。

**API 出处**: GD音乐台(music.gdstudio.xyz)

## 📊 版本历史

### v1.2.1 (2026-01-26)
- 改进歌单分类选择为文件夹形式
- 优化用户体验

### v1.2.0 (2026-01-26)
- 添加歌单功能
- 支持高质量歌单浏览
- 支持批量播放

### v1.1.0 (2026-01-26)
- 添加交互式分页功能
- 改进评论浏览体验

### v1.0.0 (2026-01-26)
- 初始版本
- 基础搜索和播放功能
- xbmcswift2 兼容

---

**最后更新**: 2026-01-26
**版本**: 1.2.1
**Kodi 版本**: 21+
**Python 版本**: 3+
