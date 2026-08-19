# cn-social-dl

> Download videos from Douyin, Xiaohongshu, Bilibili, Kuaishou, TikTok, YouTube, X and more with **one command**. **Watermark-free by default · Zero-config · Cross-platform**.

[![CI](https://github.com/renhairong/cn-social-dl/actions/workflows/ci.yml/badge.svg)](https://github.com/renhairong/cn-social-dl/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platforms](https://img.shields.io/badge/platforms-Douyin%20%7C%20XHS%20%7C%20Bilibili%20%7C%20Kuaishou%20%7C%20YouTube%20%7C%20X-blue.svg)]()

[中文文档](README.md)

---

## Table of Contents

- [Features](#features)
- [Install](#install)
- [Usage](#usage)
- [Supported platforms](#supported-platforms)
- [About cookies](#about-cookiesimportant)
- [How it works](#how-it-works)
- [Use as a WorkBuddy Skill](#use-as-a-workbuddy-skill)
- [FAQ](#faq)
- [Update & uninstall](#update--uninstall)
- [License](#license)

---

## Features

- **Douyin / Xiaohongshu** — automatically reads your **logged-in browser's** session cookies; no manual export, no third-party extensions.
- **Bilibili / TikTok / YouTube / X** and more — download **without any cookies** (yt-dlp-native support covers nearly all major platforms).
- **Kuaishou** — not supported by yt-dlp natively, so the bundled `kuaishou.py` resolves the web play URL first; it reuses your local browser's (Edge / Chrome) logged-in session to pass the anti-bot check.
- **Douyin extras: watermark-free + URL normalization** — skips the watermarked `download_addr` and prefers the clean play URL; normalizes search-page links (`?modal_id=`), short links (`v.douyin.com`), `/video/`, `/note/` automatically. Other platforms are parsed natively by yt-dlp, so they don't need these workarounds.
- **Cross-platform & no extra deps** — macOS / Linux / Windows; no dependency beyond `yt-dlp` / `ffmpeg`; compatible with the stock bash 3.2 shipped with macOS — no need to upgrade bash.

## Install

### 1. Prerequisites

You need [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) and `ffmpeg`:

```bash
# macOS
brew install yt-dlp ffmpeg

# Debian / Ubuntu
sudo apt install yt-dlp ffmpeg

# or via pip (any platform)
pip install yt-dlp
```

### 2. Install the script

<details open>
<summary><b>Option A: install as a global <code>dl</code> command (recommended)</b></summary>

Clone, then drop `dl.sh` (and `kuaishou.py` for Kuaishou) into your PATH so you can run `dl "<url>"` from anywhere:

```bash
git clone https://github.com/renhairong/cn-social-dl.git
cd cn-social-dl

# Apple Silicon (Homebrew)
cp dl.sh kuaishou.py /opt/homebrew/bin/
# or Intel Mac / Linux
# cp dl.sh kuaishou.py /usr/local/bin/

chmod +x /opt/homebrew/bin/dl /opt/homebrew/bin/kuaishou.py
```

> If you hit a permission error, prefix `cp` with `sudo`.

</details>

<details>
<summary><b>Option B: use as a project script only</b></summary>

```bash
git clone https://github.com/renhairong/cn-social-dl.git
cd cn-social-dl
bash dl.sh "VIDEO_URL"
```

</details>

## Usage

```bash
dl "VIDEO_URL"                 # if installed as a global command
bash dl.sh "VIDEO_URL"         # or as a project script
bash dl.sh "VIDEO_URL" "/dir"  # specify an output dir; defaults to ~/Downloads
```

Examples:

```bash
# Douyin (a search-page link works too — auto-normalized)
dl "https://www.douyin.com/jingxuan/search/跳舞?modal_id=7616728634532291014"

# Bilibili (no cookie needed)
dl "https://www.bilibili.com/video/BV1GJ411x7h7"

# TikTok
dl "https://www.tiktok.com/@user/video/123456"

# YouTube (public videos, no cookie — Shorts included)
dl "https://youtube.com/shorts/kkyaouUEmaU"

# X / Twitter
dl "https://x.com/username/status/1234567890/video/1"

# Kuaishou (reuses browser login session; short links v.kuaishou.com are followed automatically)
dl "https://www.kuaishou.com/short-video/3xk6y9abcde"
```

## Supported platforms

| Platform | Login required | Notes |
|---|---|---|
| Douyin / Xiaohongshu | ✅ Yes | Reads your logged-in browser session automatically |
| Kuaishou | ✅ Yes (browser session auto-detected) | Bundled `kuaishou.py` resolves the web URL; fall back to `~/.kuaishou_cookies.txt` if no browser session |
| Bilibili / TikTok | ❌ No | Download without any cookies |
| YouTube / X (Twitter) etc. | ❌ No | yt-dlp-native support covers nearly all major platforms |

> ⚠️ **Not supported yet**: WeChat Channels (视频号) and Tencent Video (腾讯视频). The former uses a private protocol with mandatory login; the latter sits behind a paid DRM wall — neither can be solved via yt-dlp pass-through in the near term.

## About cookies (important)

Douyin / Xiaohongshu / Kuaishou need a logged-in session; Bilibili / TikTok / YouTube / X need no cookies at all — they just work.

For Douyin / Xiaohongshu, cookies are resolved automatically with this priority:

1. **`DOUYIN_COOKIE_FILE` env var or `~/.douyin_cookies.txt` exists** → use that Netscape-format file directly.
2. **Otherwise, auto-detect a local browser** and read its cookies via `yt-dlp --cookies-from-browser`.

Kuaishou automatically tries to export a logged-in session from a local browser (Edge / Chrome first); if none is available, export manually to `~/.kuaishou_cookies.txt` (or set the `KUAISHOU_COOKIE` env var).

### Browser selection tips

| Browser | macOS experience | Notes |
|---|---|---|
| **Firefox** | ✅ No prompt | On macOS its cookies aren't encrypted with the system Keychain — most recommended |
| Chrome / Edge / Brave | ⚠️ First-run prompt | On macOS cookies live in the Keychain; the first run pops an authorization dialog — just allow it |
| Safari | ⚠️ Limited | yt-dlp's Safari support is weak — not recommended |

> Want to go fully browser-based with no cookie file? Just delete `~/.douyin_cookies.txt`.

### Provide a cookie file manually (optional)

If you're in an environment where browser cookies can't be read (e.g. a headless server / sandbox), export them manually:
Install the **Cookie-Editor** extension → open the target platform's page → export in Netscape format → save as `~/.douyin_cookies.txt` (or `~/.kuaishou_cookies.txt` for Kuaishou).

> Note: Douyin's session fields `sessionid_ss` / `sid_tt` are HttpOnly and cannot be read from `document.cookie` in the console — you must use an extension or `--cookies-from-browser` to export them.

## How it works

`dl.sh` is a **thin, dependency-light** wrapper on top of `yt-dlp`:

- **Douyin / Xiaohongshu**: normalize the share link → inject a cookie (file or browser) → add `-f "best[format_id!^=download_addr]/best"` so the watermarked address is excluded and the clean URL is chosen.
- **Kuaishou**: `dl.sh` short-circuits to the bundled `kuaishou.py` — a stdlib-only script that calls Kuaishou's web GraphQL endpoint for the play URL (reusing the browser login session to pass the anti-bot check), then hands it back to `yt-dlp` for download / merge.
- **Everything else**: forward the URL straight to `yt-dlp` with sensible timeouts and retries.

No login, no API keys, no background services — everything runs locally on your machine.

## Use as a WorkBuddy Skill

The repo ships a `SKILL.md` so it can be used directly as a [WorkBuddy](https://www.workbuddy.cn) skill:

```bash
# Place the repo into WorkBuddy's skills directory (restart the session to take effect)
cp -r cn-social-dl ~/.workbuddy/skills/video-downloader
```

Then just say "download this Douyin video: <url>" in a WorkBuddy conversation — the skill will call `dl.sh` automatically.

## FAQ

**Q: Kuaishou download returns empty / errors out?**
Usually the browser has no Kuaishou login session (Kuaishou shows a slider CAPTCHA to anonymous requests). Log into Kuaishou in Edge / Chrome first, then retry — the script reads the session automatically. If it still fails, export the browser Kuaishou cookies to `~/.kuaishou_cookies.txt`.

**Q: macOS pops a Keychain authorization dialog?**
The first time you read cookies from Chrome / Edge, a dialog appears — click "Allow / Always Allow". To skip the prompt entirely, log into the platform with Firefox instead.

**Q: `dl: command not found`?**
You haven't installed the global command. Either run `bash dl.sh "url"`, or put `dl.sh` into your PATH as shown in [Install](#install).

**Q: The Douyin video I got is watermarked?**
Watermark removal is the default. If a platform change breaks it, report it and the format-selection rule will be updated.

## Update & uninstall

**Update**: pull the latest code and re-sync the scripts (adjust the path to your install location):

```bash
cd cn-social-dl
git pull
cp dl.sh kuaishou.py /opt/homebrew/bin/        # or /usr/local/bin/
```

**Uninstall**:

```bash
rm -f /opt/homebrew/bin/dl /opt/homebrew/bin/kuaishou.py   # or /usr/local/bin/
```

## License

Licensed under the [MIT](LICENSE) license.
