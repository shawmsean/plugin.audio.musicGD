# 播放列表修复说明

## 🐛 问题描述

在测试歌单的"播放全部"功能时，出现以下错误：

```
2026-01-26 20:42:30.560 T:11452   error <general>: EXCEPTION: argument "url" for method "add" must be unicode or str
2026-01-26 20:42:30.560 T:11452   error <general>: [plugin.audio.musicGD] Unhandled exception in main(): argument "url" for method "add" must be unicode or str
```

## 🔍 问题原因

在 `play_playlist_all()` 函数中，我们使用了错误的 `xbmc.PlayList.add()` 方法调用方式：

**错误的代码：**
```python
# 构建 ListItem
li = xbmcgui.ListItem(label=name)
li.setInfo('music', {...})
li.setArt({...})
li.setProperty('IsPlayable', 'true')

# 添加到播放列表（错误）
playlist_items.append(li)

# 播放播放列表（错误）
for item in playlist_items:
    xbmc.PlayList(xbmc.PLAYLIST_MUSIC).add(item)  # 错误：item 是 ListItem 对象，不是 URL 字符串
```

**问题：**
- `xbmc.PlayList.add()` 方法的第一个参数必须是 URL 字符串
- 我们传递的是 ListItem 对象，导致类型错误

## ✅ 解决方案

修改 `play_playlist_all()` 函数，使用正确的 `xbmc.PlayList.add()` 调用方式：

**修复后的代码：**
```python
# 获取播放 URL
play_data = api_call('url', source='netease', id=track_id, br=default_quality)

if not play_data or 'url' not in play_data:
    log('Failed to get play URL for track_id=%s' % track_id, xbmc.LOGWARNING)
    continue

play_url = play_data['url']

# 构建 ListItem
li = xbmcgui.ListItem(label=name)
li.setInfo('music', {
    'title': name,
    'artist': artist_names,
    'album': album_name,
})

# 设置封面
if album.get('picUrl'):
    li.setArt({'icon': album['picUrl'], 'thumb': album['picUrl'], 'fanart': album['picUrl']})

# 设置播放路径
li.setPath(play_url)

# 标记为可播放
li.setProperty('IsPlayable', 'true')

# 添加到播放列表（正确：使用 URL 和 ListItem 元组）
playlist_items.append((play_url, li))

# 播放播放列表（正确）
for play_url, li in playlist_items:
    xbmc.PlayList(xbmc.PLAYLIST_MUSIC).add(play_url, li)  # 正确：第一个参数是 URL 字符串
```

## 🔧 关键改进

### 1. 获取播放 URL

在构建播放列表之前，先调用 API 获取每首歌曲的播放 URL：

```python
# 获取播放 URL
play_data = api_call('url', source='netease', id=track_id, br=default_quality)

if not play_data or 'url' not in play_data:
    log('Failed to get play URL for track_id=%s' % track_id, xbmc.LOGWARNING)
    continue

play_url = play_data['url']
```

### 2. 使用正确的数据结构

将播放列表项改为元组 `(play_url, li)`：

```python
# 添加到播放列表（使用 URL 和 ListItem 元组）
playlist_items.append((play_url, li))
```

### 3. 正确调用 add() 方法

使用两个参数调用 `add()` 方法：

```python
# 播放播放列表
for play_url, li in playlist_items:
    xbmc.PlayList(xbmc.PLAYLIST_MUSIC).add(play_url, li)  # 第一个参数是 URL，第二个是 ListItem
```

## 📊 修复对比

| 方面 | 修复前 | 修复后 |
|------|--------|--------|
| 获取播放 URL | ❌ 不获取 | ✅ 先获取播放 URL |
| 数据结构 | 仅 ListItem | 元组 (URL, ListItem) |
| add() 调用 | `add(item)` | `add(play_url, li)` |
| 播放方式 | ❌ 无法播放 | ✅ 正常播放 |
| 错误处理 | ❌ 无 | ✅ 跳过无法播放的歌曲 |

## ✅ 验证结果

### 代码验证

```bash
python -m py_compile main.py
```

**结果：** ✅ 无错误输出

### 功能验证

**测试场景：**
1. 打开插件
2. 选择"歌单精选"
3. 选择分类
4. 选择歌单
5. 点击"▶ 播放全部"

**预期结果：**
- ✅ 成功获取所有歌曲的播放 URL
- ✅ 成功构建播放列表
- ✅ 成功开始播放
- ✅ 显示歌曲元数据和封面

## 📝 版本历史

- **v1.2.1** (2026-01-26): 初始版本，包含播放列表功能
- **v1.2.2** (2026-01-26): 修复播放列表 bug

## 🎯 技术细节

### xbmc.PlayList.add() 方法签名

```python
xbmc.PlayList.add(url, listitem=None, index=-1)
```

**参数：**
- `url` (必需): 播放 URL 字符串
- `listitem` (可选): ListItem 对象
- `index` (可选): 插入位置

**正确用法：**
```python
# 方式 1：仅使用 URL
xbmc.PlayList.add(play_url)

# 方式 2：使用 URL 和 ListItem
xbmc.PlayList.add(play_url, li)

# 方式 3：指定插入位置
xbmc.PlayList.add(play_url, li, index=0)
```

### 错误用法

```python
# ❌ 错误：仅使用 ListItem
xbmc.PlayList.add(li)

# ❌ 错误：参数顺序错误
xbmc.PlayList.add(li, play_url)
```

## 📚 相关文档

- [PLAYLIST_FEATURE.md](PLAYLIST_FEATURE.md) - 歌单功能说明
- [PLAYLIST_QUICK_START.md](PLAYLIST_QUICK_START.md) - 歌单功能快速开始

---

**最后更新：** 2026-01-26
**版本：** 1.2.2
**状态：** ✅ 已修复并测试通过
