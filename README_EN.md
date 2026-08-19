# cn-social-dl

[![CI](https://github.com/renhairong/cn-social-dl/actions/workflows/ci.yml/badge.svg)](https://github.com/renhairong/cn-social-dl/actions/workflows/ci.yml)

A zero-config, cross-platform video downloader for Chinese social platforms, built on [yt-dlp](https://github.com/yt-dlp/yt-dlp).
Download videos from Douyin, Xiaohongshu, Bilibili, Kuaishou, TikTok, YouTube, X (Twitter) and more with **one command**, **watermark-free by default**.

[中文文档](README.md)

## Features

- **Douyin / Xiaohongshu**: automatically reads your **logged-in browser's** session cookies — no manual export, no third-party extensions.
- **Bilibili / TikTok / YouTube / X** and more: download **without any cookies** (yt-dlp-native support covers nearly all major platforms).
- **Kuaishou**: not supported by yt-dlp natively, so a bundled `kuaishou.py` resolves the web play URL first, then downloads it. **Public videos need no login**; if a video returns empty, drop your browser's Kuaishou cookies into `~/.kuaishou_cookies.txt`.
- **Watermark-free**: for Douyin it skips the watermarked `download_addr` and picks the clean playback URL first.
- **URL normalization**: Douyin search pages (`?modal_id=`), short links (`v.douyin.com`), `/video/`, `/note/` are all normalized automatically — just paste any link.
- **Cross-platform**: macOS / Linux / Windows, with automatic browser detection. Compatible with the stock bash 3.2 shipped with macOS — no need to upgrade bash.

## Install

You need `yt-dlp` and `ffmpeg`:

```bash
# macOS
brew install yt-dlp ffmpeg

# Debian / Ubuntu
sudo apt install yt-dlp ffmpeg

# or via pip
pip install yt-dlp
```

Then clone this repo and keep `dl.sh` wherever you like (make it executable or add to PATH):

```bash
git clone https://github.com/renhairong/cn-social-dl.git
chmod +x cn-social-dl/dl.sh
```

## Usage

```bash
bash dl.sh "VIDEO_URL"
bash dl.sh "VIDEO_URL" "/custom/output/dir"
```

When no directory is given, files are saved to `~/Downloads`.

Examples:

```bash
# Douyin (a search-page link works too — auto-normalized)
bash dl.sh "https://www.douyin.com/jingxuan/search/跳舞?modal_id=7616728634532291014"

# Bilibili (no cookie needed)
bash dl.sh "https://www.bilibili.com/video/BV1GJ411x7h7"

# TikTok
bash dl.sh "https://www.tiktok.com/@user/video/123456"

# YouTube (public videos, no cookie — Shorts included)
bash dl.sh "https://youtube.com/shorts/kkyaouUEmaU"

# X / Twitter
bash dl.sh "https://x.com/username/status/1234567890/video/1"

# Kuaishou (public videos need no login; short links v.kuaishou.com are followed automatically)
bash dl.sh "https://www.kuaishou.com/short-video/3xk6y9abcde"
```

## About cookies (important)

Only **Douyin / Xiaohongshu** require a logged-in session. **Bilibili / TikTok / Kuaishou (public videos) need no cookies at all** — they just work.

For Douyin / Xiaohongshu, cookies are resolved automatically with this priority:

1. **`DOUYIN_COOKIE_FILE` env var or `~/.douyin_cookies.txt` exists** → use that Netscape-format file directly.
2. **Otherwise, auto-detect a local browser** and read its cookies via `yt-dlp --cookies-from-browser`.

### Browser selection tips

| Browser | macOS experience | Notes |
|---|---|---|
| **Firefox** | ✅ No prompt | On macOS its cookies aren't encrypted with the system Keychain — most recommended |
| Chrome / Edge / Brave | ⚠️ First-run prompt | On macOS cookies live in the Keychain; the first run pops an authorization dialog — just allow it |
| Safari | ⚠️ Limited | yt-dlp's Safari support is weak — not recommended |

> Want to go fully browser-based with no cookie file? Just delete `~/.douyin_cookies.txt`.

### Provide a cookie file manually (optional)

If you're in an environment where browser cookies can't be read (e.g. a sandbox / headless server), export them manually:
Install the **Cookie-Editor** browser extension → open the Douyin / Xiaohongshu page → export in Netscape format → save as `~/.douyin_cookies.txt`.
(Note: Douyin's session fields `sessionid_ss` / `sid_tt` are HttpOnly and cannot be read from `document.cookie` in the console — you must use an extension or `--cookies-from-browser` to export them.)

## Use as a WorkBuddy Skill

The repo ships a `SKILL.md` so it can be used directly as a [WorkBuddy](https://www.workbuddy.cn) skill:

```bash
# Place the repo into WorkBuddy's skills directory
cp -r cn-social-dl ~/.workbuddy/skills/video-downloader
```

Then just say "download this Douyin video: <url>" in a WorkBuddy conversation — the skill will call `dl.sh` automatically.

## How it works

`dl.sh` is a thin, dependency-light wrapper around `yt-dlp`:

- It normalizes any Douyin share link (search page, short link, `/video/`, `/note/`) into a canonical `douyin.com/video/<id>` URL.
- For Douyin / Xiaohongshu it injects either a cookie file or `--cookies-from-browser`, and adds `-f "best[format_id!^=download_addr]/best"` so the watermarked download address is excluded and the clean playback URL is chosen.
- For all other platforms it simply forwards the URL to `yt-dlp` with sensible timeouts.

No login, no API keys, no background services — everything runs locally on your machine.

## License

[MIT](LICENSE)
