若使用本站提供的API，请注明出处“GD音乐台(music.gdstudio.xyz)”，尊重作者。使用过程如遇问题可B站私信：GD-Studio

当前稳定音乐源（动态更新）：netease、kuwo、joox

当前访问频率限制（动态更新）：5分钟内不超50次请求

更新日期：2025-12-3


搜索
API：https://music-api.gdstudio.xyz/api.php?types=search&source=[MUSIC SOURCE]&name=[KEYWORD]&count=[PAGE LENGTH]&pages=[PAGE NUM]

source：音乐源。可选项，参数值netease（默认）、tencent、tidal、spotify、ytmusic、qobuz、joox、deezer、migu、kugou、kuwo、ximalaya、apple。部分可能失效，建议使用稳定音乐源

* 高级用法：在音乐源后加上“_album”，如“netease_album”，可获取专辑中的曲目列表

name：关键字。必选项，关键字可以是曲目名、歌手名、专辑名

count：页面长度。可选项，一次返回显示多少内容，默认为20条

pages：页码。可选项，返回搜索结果第几页，默认为第1页

返回：id（曲目ID，即track_id）、name（歌曲名）、artist（歌手列表）、album（专辑名）、pic_id（专辑图ID）、url_id（URL ID，废弃）、lyric_id（歌词ID）、source（音乐源）


获取歌曲
API：https://music-api.gdstudio.xyz/api.php?types=url&source=[MUSIC SOURCE]&id=[TRACK ID]&br=[128/192/320/740/999]

source：音乐源。可选项，参数值netease（默认）、tencent、tidal、spotify、ytmusic、qobuz、joox、deezer、migu、kugou、kuwo、ximalaya、apple。部分可能失效，建议使用稳定音乐源

id：曲目ID。必选项，即track_id，根据音乐源不同，曲目ID的获取方式各不相同，可通过本站提供的搜索接口获取

br：音质。可选项，可选128、192、320、740、999（默认），其中740、999为无损音质

返回：url（音乐链接）、br（实际返回音质）、size（文件大小，单位为KB）


获取专辑图
API：https://music-api.gdstudio.xyz/api.php?types=pic&source=[MUSIC SOURCE]&id=[PIC ID]&size=[300/500]

source：音乐源。可选项，参数值netease（默认）、tencent、tidal、spotify、ytmusic、qobuz、joox、deezer、migu、kugou、kuwo、ximalaya、apple。部分可能失效，建议使用稳定音乐源

id：专辑图ID。必选项，专辑图ID即pic_id，可通过本站提供的搜索接口获取

size：图片尺寸。可选项，可选300（默认）、500，其中300为小图，500为大图，返回的图片不一定是300px或500px

返回：url（专辑图链接）


获取歌词
API：https://music-api.gdstudio.xyz/api.php?types=lyric&source=[MUSIC SOURCE]&id=[LYRIC ID]

source：音乐源。可选项，参数值netease（默认）、tencent、tidal、spotify、ytmusic、qobuz、joox、deezer、migu、kugou、kuwo、ximalaya、apple。部分可能失效，建议使用稳定音乐源

id：歌词ID。必选项，歌词ID即lyric_id（一般与曲目ID相同），可通过本站提供的搜索接口获取

返回：lyric（LRC格式的原语种歌词）、tlyric（LRC格式的中文翻译歌词，不一定会返回）


Kodi 21 开发的 GD 音乐台 插件设计文档摘要 — 目标是实现稳定的搜索、播放、专辑图与歌词功能，兼容 Kodi 21 插件框架，遵守 GD 音乐台署名要求并实现速率限流与离线缓存
目标与范围
目标用户：在 Kodi 21 上播放来自 GD 音乐台（GD音乐台(music.gdstudio.xyz)）的音乐内容。

核心功能：搜索、获取播放 URL、获取专辑图、获取歌词；UI 浏览、播放队列、收藏与本地缓存。

约束：必须在界面或文档中注明出处 GD音乐台(music.gdstudio.xyz)；遵守 5 分钟内不超 50 次请求 的速率限制（由 API 提供方动态更新）。

技术参考与兼容性
Kodi 插件类型：基于 Python 的音频插件，遵循 Kodi Add-on 结构与发布规范。

开发资源：参考 Kodi 开发文档与 Kodi Dev Kit 指南以确保对 Kodi 21 API 的兼容性与最佳实践。

脚本示例：可参考现有社区插件实现（如 script/addon 模式）以实现 UI 窗口与路由逻辑。

架构概览
组件：UI 层（XML 界面 + Python 控制器）；网络层（GD API 封装）；播放层（Kodi Player 控制）；缓存层（SQLite + 本地文件）。

数据流：用户输入 → 调用 GD 搜索接口 → 列表展示 → 选择曲目 → 调用 URL 接口 → 播放；并在后台异步获取专辑图与歌词并缓存。

API 映射与错误处理
映射：search → types=search；url → types=url；pic → types=pic；lyric → types=lyric。

速率控制：全局请求队列 + 令牌桶限流；遇 429 或 5xx 实施指数退避重试。

失败策略：播放回退到低码率；UI 显示友好错误并允许重试。

测试与发布
测试项：功能测试、并发限流测试、网络异常与离线缓存测试、Kodi 21 回归测试。

发布：打包为 zip，按 Kodi 插件规范提交或提供私有仓库安装说明，并在 README 明确署名 GD音乐台(music.gdstudio.xyz)。