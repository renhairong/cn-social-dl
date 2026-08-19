---
name: video-downloader
description: 通用视频下载器，支持抖音/小红书/B站/快手/TikTok 等平台。抖音/小红书自动读取本地已登录浏览器 cookie（无需手动导出），B站/TikTok/快手（公开视频）免 cookie。基于 yt-dlp，无水印优先。快手由自带 kuaishou.py 解析 web 直链。
license: MIT
---

# video-downloader

通用视频下载器，基于 [yt-dlp](https://github.com/yt-dlp/yt-dlp)，覆盖抖音 / 小红书 / B站 / 快手 / TikTok 等主流平台。

## 什么时候用
用户要下载抖音、小红书、B站、TikTok 等平台的视频（尤其「无水印」「高清」）时调用本技能，运行 `dl.sh`。

## 依赖
- **yt-dlp**（核心引擎）
- **ffmpeg**（合并 / 转封装，yt-dlp 自动调用）

安装：
- macOS：`brew install yt-dlp ffmpeg`
- 其他平台见 https://github.com/yt-dlp/yt-dlp#installation

## 用法
```bash
bash dl.sh "视频链接"
bash dl.sh "视频链接" "/自定义/保存目录"
```
不传目录时默认保存到 `~/Downloads`。

## 平台与 cookie 策略
| 平台 | 需要登录态？ | 说明 |
|---|---|---|
| B站 / TikTok / YouTube 等 | ❌ 不需要 | 免 cookie 直接下载 |
| 快手 | ✅ 需要（浏览器登录态自动读取） | 由自带 `kuaishou.py` 解析 web 直链；自动复用 Edge/Chrome 登录态过快控，无登录态时把 Cookie 写入 `~/.kuaishou_cookies.txt` |
| 抖音 / 小红书 | ✅ 需要 | 自动读取本地已登录浏览器的登录态 |

抖音 / 小红书的 cookie 获取（按优先级）：
1. 若环境变量 `DOUYIN_COOKIE_FILE` 指向的文件、或 `~/.douyin_cookies.txt` 存在 → 直接用该 Netscape 文件。
2. 否则自动探测本地浏览器，用 `--cookies-from-browser <浏览器>` 读取（**推荐 Firefox**：macOS 上不依赖系统 Keychain，零弹窗；Chrome/Edge 在 macOS 首次需 Keychain 授权弹窗）。

> 想纯粹走「浏览器自动读取」、完全不依赖 cookie 文件？删掉 `~/.douyin_cookies.txt` 即可。

## 无水印
抖音默认排除带水印的 `download_addr`，优先选 `play_addr` 无水印直链（格式选择 `best[format_id!^=download_addr]/best`）。

## 链接归一化
抖音搜索页（`?modal_id=`）、分享短链（`v.douyin.com`）、`/video/`、`/note/` 链接均自动归一化为标准 video 链接，无需手动改 URL。
