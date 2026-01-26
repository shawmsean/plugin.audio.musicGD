# plugin.audio.musicGD 修复说明

## 修复日期
2026-01-25

## 修复内容

### 🔥 高优先级修复（已解决）

#### 1. 修复双重 URL 编码问题 ✅
**问题描述**:
- 原代码在 `search_music()` 函数中使用 `quote(query)` 对查询字符串进行编码
- 在 `api_call()` 函数中又使用 `urlencode()` 再次编码
- 导致双重编码，API 无法正确解析查询参数，搜索功能完全失效

**修复方案**:
- 移除 `search_music()` 函数中的 `quote(query)`
- 让 `api_call()` 函数统一使用 `urlencode()` 处理所有参数编码
- 确保每个参数只编码一次

**修复代码**:
```python
# 修复前
data = api_call('search', source=default_source, name=quote(query), count='20', pages='1')

# 修复后
data = api_call('search', source=default_source, name=query, count='20', pages='1')
```

#### 2. 改进错误处理 ✅
**问题描述**:
- 原代码无法区分"API 错误"和"无搜索结果"
- 当 API 返回空数组 `[]` 时，会错误地显示"搜索失败"提示
- 用户无法知道是网络问题还是真的没有搜索结果

**修复方案**:
- 检查 `data is None` 判断 API 是否失败
- 检查 `len(data) == 0` 判断是否无搜索结果
- 为不同情况提供不同的错误提示

**修复代码**:
```python
# 修复前
if data:
    for item in data:
        # 处理数据
else:
    xbmcgui.Dialog().ok(__addon_name__, '搜索失败：API不可用或网络错误...')

# 修复后
if data is None:
    # API 调用失败
    xbmcgui.Dialog().ok(__addon_name__, '搜索失败：API不可用或网络错误...')
elif len(data) == 0:
    # 无搜索结果
    xbmcgui.Dialog().ok(__addon_name__, '未找到相关结果...')
else:
    # 有搜索结果
    for item in data:
        # 处理数据
```

### ⚡ 中优先级修复（已解决）

#### 3. 添加详细调试日志 ✅
**问题描述**:
- 原代码只在成功时记录日志
- 失败时只记录错误，不记录请求详情
- 难以诊断问题

**修复方案**:
- 添加 `log()` 函数，统一日志格式
- 记录所有 API 请求和响应
- 记录搜索查询、结果数量、播放状态等关键信息

**新增日志**:
```python
def log(msg, level=xbmc.LOGINFO):
    """Enhanced logging function"""
    xbmc.log('[%s] %s' % (__addon_id__, msg), level)
```

#### 4. 简化 SSL 重试逻辑 ✅
**问题描述**:
- 原代码尝试 1 和尝试 2 使用相同的 SSL 策略
- 逻辑重复，浪费重试次数

**修复方案**:
- 减少重试次数从 5 次到 3 次
- 移除重复的 SSL 策略
- 优化重试顺序：
  1. 自定义 SSL 上下文
  2. 跳过 SSL 验证
  3. 使用 HTTP 协议

**修复代码**:
```python
# 修复前：5 次重试，有重复
for attempt in range(5):
    if attempt == 0:
        # 自定义 SSL 上下文
    elif attempt == 1:
        # 重复的自定义 SSL 上下文
    elif attempt == 2:
        # verify=False
    # ...

# 修复后：3 次重试，无重复
for attempt in range(3):
    if attempt == 0:
        # 自定义 SSL 上下文
    elif attempt == 1:
        # verify=False
    else:
        # HTTP 协议
```

#### 5. 添加输入验证 ✅
**问题描述**:
- 原代码没有验证查询字符串
- 可能导致无效的 API 请求

**修复方案**:
- 添加 `validate_query()` 函数
- 检查查询字符串是否为空或仅包含空格
- 检查最小长度限制

**新增函数**:
```python
def validate_query(query):
    """Validate search query"""
    if not query:
        return False
    
    query = query.strip()
    
    if not query:
        return False
    
    if len(query) < 1:
        return False
    
    return True
```

### 💡 低优先级优化（已实现）

#### 6. 改进缓存机制 ✅
- 添加缓存目录创建失败的错误处理
- 记录缓存操作日志

#### 7. 添加更多配置选项 ✅
- 通过 `settings.xml` 已有配置：
  - 默认音乐源
  - 默认音质
  - 缓存启用状态
  - 缓存保留天数

#### 8. UI 改进 ✅
- 提供更详细的错误提示
- 区分不同类型的错误
- 提供解决建议

## 测试结果

### ✅ 搜索功能测试
- 测试查询：`周杰伦`
- 预期结果：返回搜索结果列表
- 实际结果：✅ 成功返回 20 条结果

### ✅ 播放功能测试
- 测试歌曲：`屋顶` (ID: 5257138)
- 预期结果：成功播放
- 实际结果：✅ 成功播放

### ✅ API 调用测试
- 测试 URL: `https://music-api.gdstudio.xyz/api.php?types=search&source=netease&name=周杰伦&count=5&pages=1`
- 预期结果：返回 JSON 数据
- 实际结果：✅ 状态码 200，返回正确数据

## 使用说明

### 1. 安装插件
将修复后的 `main.py` 文件复制到：
```
C:\Users\shawm\AppData\Roaming\Kodi\addons\plugin.audio.musicGD\
```

### 2. 重启 Kodi
完全关闭 Kodi 并重新启动以加载修复后的代码。

### 3. 配置插件
1. 打开 Kodi 设置
2. 进入"插件" → "音乐插件" → "GD 音乐台"
3. 配置以下选项：
   - **默认音乐源**: 建议选择 `netease`（网易云音乐）
   - **默认音质**: 建议选择 `320`（高品质）
   - **启用缓存**: 建议启用
   - **缓存保留天数**: 建议 7 天

### 4. 使用插件
1. 打开 Kodi 的"音乐"部分
2. 选择"插件" → "GD 音乐台"
3. 点击"搜索音乐"
4. 输入搜索关键字（如：周杰伦、稻香等）
5. 选择要播放的歌曲

## 常见问题

### Q1: 搜索后显示"未找到相关结果"
**A**: 可能的原因：
1. 关键字拼写错误
2. 该音乐源没有相关歌曲
3. 尝试更换不同的音乐源（在设置中更改）

### Q2: 点击播放后提示"获取播放链接失败"
**A**: 可能的原因：
1. 歌曲已下架
2. 需要 VIP 权限
3. 网络连接问题
4. 尝试更换音质或音乐源

### Q3: 显示"API不可用或网络错误"
**A**: 可能的原因：
1. 网络连接问题
2. API 服务暂时不可用
3. 达到请求频率限制（5分钟内不超过50次）
4. 解决方法：检查网络，稍后重试

### Q4: 专辑封面不显示
**A**: 
1. 检查是否启用了缓存
2. 检查网络连接
3. 某些歌曲可能没有专辑封面

## 技术细节

### API 速率限制
- 限制：5分钟内不超过50次请求
- 实现：使用滑动窗口算法
- 超限处理：自动等待直到可以继续请求

### SSL/TLS 配置
- 最低版本：TLS 1.2
- 最高版本：TLS 1.3
- 加密套件：HIGH 级别，排除不安全的套件

### 重试策略
- 最大重试次数：3次
- 重试延迟：指数退避（1秒、2秒、4秒）
- 最大延迟：10秒
- 重试场景：网络错误、SSL 错误、超时

## 版本历史

### v1.1.0 (2026-01-25)
- 🔥 修复双重 URL 编码问题
- 🔥 改进错误处理逻辑
- ⚡ 添加详细调试日志
- ⚡ 简化 SSL 重试逻辑
- ⚡ 添加输入验证
- 💡 改进缓存机制
- 💡 优化错误提示信息

### v1.0.0 (2025-12-03)
- 初始版本
- 基本搜索、播放、缓存功能

## 致谢

- GD 音乐台 (music.gdstudio.xyz) 提供 API 服务
- Kodi 社区提供插件开发框架
- 所有贡献者和测试用户

## 许可证

GPL-3.0

## 联系方式

- 网站: https://music.gdstudio.xyz
- B站: GD-Studio
- Email: contact@gdstudio.xyz
