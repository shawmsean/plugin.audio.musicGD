# plugin.audio.musicGD 紧急修复说明

## 问题诊断

根据日志分析，发现以下问题：

### 🔴 核心问题：JSON 解析失败

**错误信息**:
```
[plugin.audio.musicGD] API error on attempt 1/3: Expecting value: line 1 column 1 (char 0)
```

**原因分析**:
1. API 实际返回了正确的 JSON 数据（通过直接测试验证）
2. 但插件在解析 `response.json()` 时失败
3. 可能的原因：
   - 响应包含额外的空行或 BOM 字符
   - 响应编码问题
   - Accept-Encoding 包含 'br' 导致响应压缩格式不兼容

## 修复方案

### 1. 简化 Accept-Encoding 头 ✅
**问题**: `Accept-Encoding: gzip, deflate, br` 中的 `br` (Brotli) 压缩可能导致兼容性问题

**修复**:
```python
# 修复前
'Accept-Encoding': 'gzip, deflate, br',

# 修复后
'Accept-Encoding': 'gzip, deflate',
```

### 2. 添加详细的响应日志 ✅
**问题**: 无法诊断 JSON 解析失败的具体原因

**修复**:
```python
# 添加响应详情日志
log('Response status: %d' % response.status_code)
log('Response content type: %s' % response.headers.get('Content-Type', 'unknown'))
log('Response content length: %d bytes' % len(response.content))

# 检查空响应
if not response.content:
    log('API returned empty response', xbmc.LOGERROR)
    continue

# 记录响应预览
response_preview = response.text[:200] if response.text else ''
log('Response preview: %s' % response_preview)

# 单独捕获 JSON 解析错误
try:
    data = response.json()
except ValueError as json_error:
    log('JSON parsing failed: %s' % str(json_error), xbmc.LOGERROR)
    log('Full response text: %s' % response.text[:500], xbmc.LOGERROR)
    continue
```

### 3. 移除不必要的请求头 ✅
**问题**: 某些请求头可能被 API 服务器拒绝

**修复**:
```python
# 移除的请求头
# 'Upgrade-Insecure-Requests': '1',
# 'Sec-Fetch-Dest': 'empty',
# 'Sec-Fetch-Mode': 'cors',
# 'Sec-Fetch-Site': 'same-origin',

# 添加的请求头
'Cache-Control': 'no-cache',
'Pragma': 'no-cache',
```

## 测试步骤

### 1. 应用修复
将修复后的 `main.py` 文件复制到插件目录：
```
C:\Users\shawm\AppData\Roaming\Kodi\addons\plugin.audio.musicGD\
```

### 2. 重启 Kodi
完全关闭并重新启动 Kodi。

### 3. 启用调试日志
1. 打开 Kodi 设置
2. 进入"系统" → "日志"
3. 勾选"记录调试日志"
4. 设置日志级别为"调试"

### 4. 测试搜索功能
1. 进入"音乐" → "插件" → "GD 音乐台"
2. 点击"搜索音乐"
3. 输入：`晴天`
4. 点击确认

### 5. 检查日志
打开日志文件：
```
C:\Users\shawm\AppData\Roaming\Kodi\kodi.log
```

搜索以下内容：
```
[plugin.audio.musicGD] Response status:
[plugin.audio.musicGD] Response content type:
[plugin.audio.musicGD] Response preview:
```

## 预期日志输出

### ✅ 成功情况
```
[plugin.audio.musicGD] Searching for: 晴天
[plugin.audio.musicGD] Using music source: netease
[plugin.audio.musicGD] API Request: https://music-api.gdstudio.xyz/api.php?...
[plugin.audio.musicGD] Response status: 200
[plugin.audio.musicGD] Response content type: application/json
[plugin.audio.musicGD] Response content length: 4521 bytes
[plugin.audio.musicGD] Response preview: [{"id":"2652820720","name":"晴天(深情版)",...
[plugin.audio.musicGD] API success on attempt 1
[plugin.audio.musicGD] API returned 20 items
[plugin.audio.musicGD] Found 20 results
```

### ❌ 失败情况
```
[plugin.audio.musicGD] Response status: 200
[plugin.audio.musicGD] Response content type: text/html
[plugin.audio.musicGD] Response content length: 1234 bytes
[plugin.audio.musicGD] Response preview: <!DOCTYPE html>...
[plugin.audio.musicGD] JSON parsing failed: Expecting value: line 1 column 1
[plugin.audio.musicGD] API error on attempt 1/3: ...
```

## 如果仍然失败

### 方案 1: 使用 HTTP 协议
如果 HTTPS 有问题，可以强制使用 HTTP：

```python
# 在 api_call 函数中，将 BASE_URL 改为：
BASE_URL = 'http://music-api.gdstudio.xyz/api.php'
```

### 方案 2: 检查代理设置
如果你使用了代理，可能在 Kodi 中配置代理或系统代理。

### 方案 3: 联系 API 提供方
如果所有方法都失败，可能是 API 服务端的问题：
- 网站: https://music.gdstudio.xyz
- B站: GD-Studio

## 验证 API 可用性

### 使用 curl 测试
```bash
curl -v "https://music-api.gdstudio.xyz/api.php?types=search&source=netease&name=晴天&count=5&pages=1"
```

### 使用 Python 测试
```python
import requests

url = "https://music-api.gdstudio.xyz/api.php"
params = {
    'types': 'search',
    'source': 'netease',
    'name': '晴天',
    'count': '5',
    'pages': '1'
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
}

response = requests.get(url, params=params, headers=headers)
print("Status:", response.status_code)
print("Content-Type:", response.headers.get('Content-Type'))
print("Response:", response.text[:500])
```

## 版本信息

- **修复版本**: v1.2.0
- **修复日期**: 2026-01-25
- **修复内容**:
  - 修复 JSON 解析失败问题
  - 简化 HTTP 请求头
  - 添加详细的调试日志
  - 改进错误处理

## 致谢

感谢您提供的详细日志，这对问题诊断非常有帮助！

---

**如果问题仍然存在，请提供最新的 Kodi 日志内容。**
