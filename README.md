# cn-social-dl

> 一行命令，下载抖音、小红书、B站、快手、TikTok、YouTube、X 等平台的视频。**无水印优先 · 零配置 · 跨平台**。

[![CI](https://github.com/renhairong/cn-social-dl/actions/workflows/ci.yml/badge.svg)](https://github.com/renhairong/cn-social-dl/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platforms](https://img.shields.io/badge/platforms-Douyin%20%7C%20XHS%20%7C%20Bilibili%20%7C%20Kuaishou%20%7C%20YouTube%20%7C%20X-blue.svg)]()

[English](README_EN.md)

---

## 目录

- [特性](#特性)
- [安装](#安装)
- [用法](#用法)
- [支持平台](#支持平台)
- [关于 cookie](#关于-cookie重要)
- [工作原理](#工作原理)
- [作为 WorkBuddy Skill 使用](#作为-workbuddy-skill-使用)
- [常见问题](#常见问题)
- [更新与卸载](#更新与卸载)
- [许可证](#许可证)

---

## 特性

- **抖音 / 小红书** — 自动读取本地**已登录浏览器**的登录态 cookie，**无需手动导出、无需第三方扩展**。
- **B站 / TikTok / YouTube / X 等** — 免 cookie，直接下载（基于 yt-dlp 原生支持，几乎覆盖所有主流平台）。
- **快手** — yt-dlp 原生不支持，由自带的 `kuaishou.py` 解析 web 直链；自动复用本地浏览器（Edge / Chrome）登录态过快控。
- **抖音特判：无水印 + 链接归一化** — 默认排除带水印的 `download_addr`、优先选无水印直链；抖音搜索页（`?modal_id=`）、分享短链（`v.douyin.com`）、`/video/`、`/note/` 自动归一化。其他平台由 yt-dlp 原生解析，输出本身就是无水印直链。
- **跨平台 & 零额外依赖** — macOS / Linux / Windows；除 `yt-dlp` / `ffmpeg` 外无额外依赖；兼容 macOS 自带的 bash 3.2（无需升级 bash）。

## 安装

### 1. 前置依赖

需要 [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) 和 `ffmpeg`：

```bash
# macOS
brew install yt-dlp ffmpeg

# Debian / Ubuntu
sudo apt install yt-dlp ffmpeg

# 或用 pip（任意平台）
pip install yt-dlp
```

### 2. 安装脚本

<details open>
<summary><b>方式一：装成全局 <code>dl</code> 命令（推荐）</b></summary>

克隆后把 `dl.sh`（及快手所需的 `kuaishou.py`）放进 PATH，即可在任意终端直接 `dl "<链接>"`：

```bash
git clone https://github.com/renhairong/cn-social-dl.git
cd cn-social-dl

# Apple Silicon (Homebrew)
cp dl.sh kuaishou.py /opt/homebrew/bin/
# 或 Intel Mac / Linux
# cp dl.sh kuaishou.py /usr/local/bin/

chmod +x /opt/homebrew/bin/dl /opt/homebrew/bin/kuaishou.py
```

> 若提示权限不足，在 `cp` 前加 `sudo`。

</details>

<details>
<summary><b>方式二：仅作为项目脚本</b></summary>

```bash
git clone https://github.com/renhairong/cn-social-dl.git
cd cn-social-dl
bash dl.sh "视频链接"
```

</details>

## 用法

```bash
dl "视频链接"                 # 已装全局命令时
bash dl.sh "视频链接"         # 或作为项目脚本
bash dl.sh "视频链接" "/目录"  # 指定保存目录；不传则默认 ~/Downloads
```

示例：

```bash
# 抖音（搜索页链接也行，会自动归一化）
dl "https://www.douyin.com/jingxuan/search/跳舞?modal_id=7616728634532291014"

# B站（免 cookie）
dl "https://www.bilibili.com/video/BV1GJ411x7h7"

# TikTok
dl "https://www.tiktok.com/@user/video/123456"

# YouTube（公开视频免 cookie，含 Shorts）
dl "https://youtube.com/shorts/kkyaouUEmaU"

# X / Twitter
dl "https://x.com/username/status/1234567890/video/1"

# 快手（自动复用浏览器登录态；短链 v.kuaishou.com 会自动跟随重定向）
dl "https://www.kuaishou.com/short-video/3xk6y9abcde"
```

## 支持平台

| 平台 | 需要登录态 | 说明 |
|---|---|---|
| 抖音 / 小红书 | ✅ 需要 | 自动读取本地已登录浏览器的登录态 |
| 快手 | ✅ 需要（浏览器登录态自动读取） | 自带 `kuaishou.py` 解析 web 直链；无浏览器登录态时把 Cookie 写入 `~/.kuaishou_cookies.txt` |
| B站 / TikTok | ❌ 不需要 | 免 cookie 直接下载 |
| YouTube / X(Twitter) 等 | ❌ 不需要 | yt-dlp 原生支持，几乎覆盖所有主流平台 |

> ⚠️ **暂不支持**：微信视频号、腾讯视频。前者是私协议 + 强登录态，后者是付费墙 DRM，短期内无法用 yt-dlp 透传解决。

## 关于 cookie（重要）

抖音 / 小红书 / 快手需要登录态；B站 / TikTok / YouTube / X 不需要任何 cookie，直接下。

抖音 / 小红书的 cookie 按以下优先级自动处理：

1. **环境变量 `DOUYIN_COOKIE_FILE` 或 `~/.douyin_cookies.txt` 存在** → 直接用该 Netscape 格式文件。
2. **否则自动探测本地浏览器**，用 `yt-dlp --cookies-from-browser` 读取已登录的浏览器 cookie。

快手则会自动尝试从本地浏览器（Edge / Chrome 优先）导出登录态 cookie；若都没有，可手动导出到 `~/.kuaishou_cookies.txt`（或设 `KUAISHOU_COOKIE` 环境变量）。

### 浏览器选择建议

| 浏览器 | macOS 体验 | 说明 |
|---|---|---|
| **Firefox** | ✅ 零弹窗 | macOS 上 cookie 不依赖系统 Keychain，最推荐 |
| Chrome / Edge / Brave | ⚠️ 首次需授权 | macOS 上 cookie 用 Keychain 加密，首次运行会弹授权窗，允许即可 |
| Safari | ⚠️ 有限支持 | yt-dlp 对 Safari 支持较弱，不推荐 |

> 想完全不依赖 cookie 文件、纯浏览器自动读取？删掉 `~/.douyin_cookies.txt` 即可。

### 手动提供 cookie 文件（可选）

若处于无法读取浏览器 cookie 的环境（例如无 GUI 服务器 / 沙箱），可手动导出：
浏览器装 **Cookie-Editor** 扩展 → 打开对应平台网页 → 导出 Netscape 格式 → 存为 `~/.douyin_cookies.txt`（快手则存 `~/.kuaishou_cookies.txt`）。

> 注意：抖音的登录态字段 `sessionid_ss` / `sid_tt` 是 HttpOnly，控制台 `document.cookie` 读不到，必须用扩展或 `--cookies-from-browser` 导出。

## 工作原理

`dl.sh` 是 `yt-dlp` 之上一个**轻量、零额外依赖**的封装：

- **抖音 / 小红书**：归一化分享链接 → 注入 cookie（文件或浏览器）→ 加 `-f "best[format_id!^=download_addr]/best"` 排除带水印地址、优先无水印直链。
- **快手**：`dl.sh` 短路调用自带的 `kuaishou.py` —— 用标准库请求快手 web GraphQL 接口拿直链（自动复用浏览器登录态过快控），再交回 `yt-dlp` 下载 / 合并。
- **其余平台**：直接把链接转发给 `yt-dlp`，附上合理的超时与重试。

无登录、无 API key、无后台服务 —— 一切都在你本机本地运行。

## 作为 WorkBuddy Skill 使用

仓库根目录自带 `SKILL.md`，可直接作为 [WorkBuddy](https://www.workbuddy.cn) 技能使用：

```bash
# 把仓库放进 WorkBuddy 的技能目录（重开会话后生效）
cp -r cn-social-dl ~/.workbuddy/skills/video-downloader
```

之后在 WorkBuddy 对话中直接说「下载这个抖音视频：<链接>」即可，技能会自动调用 `dl.sh`。

## 常见问题

**Q：快手下载返回空 / 报错？**
多半是浏览器里没有快手登录态（快手对匿名请求会弹滑块风控）。先在 Edge / Chrome 登录快手，再重试；脚本会自动读取登录态。仍不行就把浏览器快手 Cookie 导出到 `~/.kuaishou_cookies.txt`。

**Q：macOS 弹出 Keychain 授权窗？**
首次用 Chrome / Edge 读取 cookie 会弹窗，点「允许 / 始终允许」即可。想彻底免弹窗，改用 Firefox 登录对应平台。

**Q：`dl: command not found`？**
说明没装全局命令。要么用 `bash dl.sh "链接"`，要么按[安装](#安装)把 `dl.sh` 放进 PATH。

**Q：抖音下了带水印的版本？**
默认去水印。若平台改版导致失效，反馈即可，会同步调整格式选择规则。

## 更新与卸载

**更新**：拉取最新代码并重新同步脚本（路径按你的实际安装位置调整）

```bash
cd cn-social-dl
git pull
cp dl.sh kuaishou.py /opt/homebrew/bin/        # 或 /usr/local/bin/
```

**卸载**：

```bash
rm -f /opt/homebrew/bin/dl /opt/homebrew/bin/kuaishou.py   # 或 /usr/local/bin/
```

## 许可证

基于 [MIT](LICENSE) 许可证开源。
