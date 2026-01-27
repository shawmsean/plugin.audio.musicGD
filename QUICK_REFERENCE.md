# 缓存系统快速参考指南

## 🚀 快速开始

### 1. 启用缓存
在插件设置中确保 `cache_enabled` 选项为 `true`

### 2. 查看缓存
进入主菜单 → 点击"缓存管理" → 查看缓存统计信息

### 3. 清理缓存
- **清理过期缓存**: 缓存管理界面 → "清理过期缓存"
- **清理所有缓存**: 缓存管理界面 → "清理所有缓存" → 确认

## 📋 缓存内容速查

| 缓存类型 | 缓存键格式 | 过期时间 | 影响范围 |
|---------|-----------|---------|---------|
| 歌单标签 | `playlist_tags` | 24小时 | 歌单分类页面 |
| 歌单列表 | `highquality_playlists_{cat}_{offset}_{limit}` | 24小时 | 各分类歌单列表 |
| 歌单详情 | `playlist_detail_{playlist_id}` | 24小时 | 歌单详情页面 |
| 歌单歌曲 | `playlist_all_tracks_{playlist_id}_{offset}_{limit}` | 24小时 | 歌单内歌曲列表 |

## 🔧 API 函数速查

### 使用缓存 (默认)
```python
data = get_playlist_tags()
data = get_highquality_playlists(cat='全部', limit=20, offset=0)
data = get_playlist_detail(playlist_id='12345')
data = get_playlist_all_tracks(playlist_id='12345')
```

### 不使用缓存 (强制从 API 获取)
```python
data = get_playlist_tags(use_cache=False)
data = get_highquality_playlists(cat='全部', limit=20, offset=0, use_cache=False)
data = get_playlist_detail(playlist_id='12345', use_cache=False)
data = get_playlist_all_tracks(playlist_id='12345', use_cache=False)
```

## 🛠️ 缓存管理函数

### 查看缓存信息
```python
cache_info = get_cache_info()
# 返回: {'total_files': 10, 'expired_files': 2, 'valid_files': 8, 'total_size_mb': 1.5}
```

### 清理过期缓存
```python
deleted_count = clear_expired_cache()
# 返回: 删除的文件数量
```

### 清理所有缓存
```python
deleted_count = clear_all_cache()
# 返回: 删除的文件数量
```

## 📊 缓存统计信息

### 显示内容
- 缓存状态 (已启用/已禁用)
- 缓存过期时间 (24小时)
- 总缓存文件数
- 有效缓存文件数
- 过期缓存文件数
- 缓存总大小 (MB)

## 💡 使用技巧

### 1. 首次加载慢?
- 这是正常现象,首次访问需要从 API 获取数据
- 后续访问会使用缓存,速度会显著提升

### 2. 想要最新数据?
- 使用"清理所有缓存"功能
- 等待 24 小时后自动刷新

### 3. 网络不稳定?
- 缓存功能会自动使用本地缓存
- 即使网络失败也能正常显示数据

### 4. 缓存占用空间大?
- 使用"清理过期缓存"功能
- 定期清理可保持缓存大小在合理范围

## 🐛 常见问题

### Q: 缓存未生效?
A: 检查插件设置中的 `cache_enabled` 是否为 `true`

### Q: 显示旧数据?
A: 使用"清理所有缓存"功能强制刷新

### Q: 缓存文件在哪里?
A: `special://profile/addon_data/plugin.audio.musicGD/cache/`

### Q: 如何禁用缓存?
A: 在插件设置中将 `cache_enabled` 改为 `false`

## 📈 性能对比

### 无缓存
- 每次访问: 1 次 API 请求
- 加载速度: 取决于网络
- 弱网体验: 较差

### 有缓存
- 首次访问: 1 次 API 请求
- 再次访问: 0 次 API 请求
- 加载速度: < 100ms
- 弱网体验: 良好

## 🔍 调试技巧

### 查看日志
在 Kodi 日志中搜索 `[plugin.audio.musicGD]` 查看缓存相关日志:

```
[plugin.audio.musicGD] Cache hit: playlist_tags
[plugin.audio.musicGD] Using cached playlist tags
[plugin.audio.musicGD] Cache written: highquality_playlists_全部_0_20
[plugin.audio.musicGD] Cache expired: playlist_detail_12345
[plugin.audio.musicGD] Auto-cleared 3 expired cache files on startup
```

### 测试缓存功能
运行测试脚本:
```bash
python test_cache.py
```

## 📞 获取帮助

- 查看详细文档: `CACHE_SYSTEM_README.md`
- 查看实现总结: `IMPLEMENTATION_SUMMARY.md`
- 提交问题: GitHub Issues

---

**快速提示**: 缓存功能默认已启用,无需额外配置即可享受加速效果!
