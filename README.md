# cn-social-dl

[English](README_EN.md)

一个零配置、跨平台的通用视频下载器，基于 [yt-dlp](https://github.com/yt-dlp/yt-dlp)。
一行命令下载抖音、小红书、B站、TikTok 等平台的视频，**无水印优先**。

## 特性

- **抖音 / 小红书**：自动读取你本地**已登录浏览器**的登录态 cookie，**无需手动导出、无需第三方扩展**。
- **B站 / TikTok / YouTube 等**：免 cookie，直接下载。
- **无水印**：抖音默认排除带水印的下载地址，优先选无水印直链。
- **链接自适应**：抖音搜索页（`?modal_id=`）、分享短链（`v.douyin.com`）、`/video/`、`/note/` 都自动归一化，随手粘就行。
- **跨平台**：macOS / Linux / Windows，自动探测本地浏览器。

## 安装

需要 `yt-dlp` 和 `ffmpeg`：

```bash
# macOS
brew install yt-dlp ffmpeg

# Debian/Ubuntu
sudo apt install yt-dlp ffmpeg

# 或用 pip
pip install yt-dlp
```

然后克隆本仓库，把 `dl.sh` 放到任意位置（建议加执行权限或放进 PATH）：

```bash
git clone https://github.com/renhairong/cn-social-dl.git
chmod +x cn-social-dl/dl.sh
```

## 用法

```bash
bash dl.sh "视频链接"
bash dl.sh "视频链接" "/自定义/保存目录"
```

不传目录时默认保存到 `~/Downloads`。

示例：

```bash
# 抖音（搜索页链接也行，会自动归一化）
bash dl.sh "https://www.douyin.com/jingxuan/search/跳舞?modal_id=7616728634532291014"

# B站（免 cookie）
bash dl.sh "https://www.bilibili.com/video/BV1GJ411x7h7"

# TikTok
bash dl.sh "https://www.tiktok.com/@user/video/123456"
```

## 关于 cookie（重要）

只有**抖音 / 小红书**需要登录态；**B站 / TikTok 不需要任何 cookie**，直接下。

抖音 / 小红书的 cookie 获取按以下优先级自动处理：

1. **环境变量 `DOUYIN_COOKIE_FILE` 或 `~/.douyin_cookies.txt` 存在** → 直接用该 Netscape 格式文件。
2. **否则自动探测本地浏览器**，用 `yt-dlp --cookies-from-browser` 读取你已登录的浏览器 cookie。

### 浏览器选择建议

| 浏览器 | macOS 体验 | 说明 |
|---|---|---|
| **Firefox** | ✅ 零弹窗 | macOS 上 cookie 不依赖系统 Keychain，最推荐 |
| Chrome / Edge / Brave | ⚠️ 首次需授权 | macOS 上 cookie 用 Keychain 加密，首次运行会弹授权窗，允许即可 |
| Safari | ⚠️ 有限支持 | yt-dlp 对 Safari 支持较弱，不推荐 |

> 想完全不依赖 cookie 文件、纯浏览器自动读取？删掉 `~/.douyin_cookies.txt` 即可。

### 手动提供 cookie 文件（可选）

如果你处于无法读取浏览器 cookie 的环境（例如某些沙箱 / 无 GUI 服务器），可手动导出：
浏览器装 **Cookie-Editor** 扩展 → 打开抖音/小红书网页 → 导出 Netscape 格式 → 存为 `~/.douyin_cookies.txt`。
（注意：抖音的登录态字段 `sessionid_ss` / `sid_tt` 是 HttpOnly，控制台 `document.cookie` 读不到，必须用扩展或 `--cookies-from-browser` 导出。）

## 作为 WorkBuddy Skill 使用

仓库根目录自带 `SKILL.md`，可直接作为 WorkBuddy 技能使用：

```bash
# 把仓库放到 WorkBuddy 的 skills 目录
cp -r cn-social-dl ~/.workbuddy/skills/video-downloader
```

之后在 WorkBuddy 对话中直接说「下载这个抖音视频：<链接>」即可，技能会自动调用 `dl.sh`。

## 许可证

[MIT](LICENSE)
