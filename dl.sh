#!/usr/bin/env bash
# dl —— 通用视频下载器（抖音 / 小红书 / B站 / TikTok …）
#
# 零配置：抖音/小红书自动读取本地已登录浏览器的登录态 cookie；
#         B站/TikTok 等免 cookie 直接下载。
#
# 依赖: yt-dlp + ffmpeg（需自行安装：brew install yt-dlp ffmpeg）
# 用法:
#   dl "视频链接"
#   dl "视频链接" "/自定义/保存目录"
#
# 抖音/小红书 cookie 获取优先级：
#   1) 环境变量 DOUYIN_COOKIE_FILE 或 ~/.douyin_cookies.txt 存在 → 直接用文件
#   2) 否则自动探测本地浏览器，用 --cookies-from-browser 读取
#      （推荐 Firefox：macOS 上不依赖系统 Keychain，零弹窗；
#       Chrome/Edge 在 macOS 上首次需 Keychain 授权弹窗）
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
URL="${1:?用法: dl <视频链接> [保存目录]}"
OUT="${2:-$HOME/Downloads}"
CF="${DOUYIN_COOKIE_FILE:-$HOME/.douyin_cookies.txt}"
YTDLP="$(command -v yt-dlp 2>/dev/null || echo /opt/homebrew/bin/yt-dlp)"
mkdir -p "$OUT"

# 抖音：任意分享链接（搜索页 ?modal_id=、/video/、/note/、v.douyin.com 短链）
# 统一归一化为标准 video 链接，yt-dlp 才能识别。
if [[ "$URL" == *douyin.com* || "$URL" == *v.douyin.com* ]]; then
  ID="$(echo "$URL" | grep -oE '(modal_id=|/video/|/note/)[0-9]+' | grep -oE '[0-9]+' | head -1 || true)"
  [[ -n "$ID" ]] && URL="https://www.douyin.com/video/$ID"
fi

# 快手：yt-dlp 原生不支持，走自带的 kuaishou.py 解析直链后交给 yt-dlp 下载/合并
if [[ "$URL" == *kuaishou.com* || "$URL" == *v.kuaishou.com* ]]; then
  PY="$(command -v python3 || command -v python)"
  MAP="$("$PY" "$SCRIPT_DIR/kuaishou.py" "$URL" 2>/tmp/kuaishou.err)" || {
    echo "❌ 快手解析失败：" >&2
    sed 's/^/    /' /tmp/kuaishou.err >&2
    echo "    已自动尝试读取本地浏览器（Edge/Chrome）的快手登录态，仍失败。" >&2
    echo "    请确认浏览器已登录快手；或把 Netscape 格式 cookie 放到 ~/.kuaishou_cookies.txt 后重试。" >&2
    exit 1
  }
  TITLE="$(printf '%s\n' "$MAP" | sed -n '1p')"
  MEDIA="$(printf '%s\n' "$MAP" | sed -n '2p')"
  exec "$YTDLP" \
    --socket-timeout 30 \
    --no-check-certificates \
    --no-playlist \
    -o "$OUT/${TITLE} [kuaishou].%(ext)s" \
    "$MEDIA"
fi

# 探测本地已安装的浏览器（优先 Firefox，macOS 上不依赖 Keychain）
detect_browser() {
  local b app name
  case "$(uname -s)" in
    Darwin)
      for b in "Firefox.app:firefox" "Google Chrome.app:chrome" "Microsoft Edge.app:edge" \
               "Brave Browser.app:brave" "Chromium.app:chromium" "Safari.app:safari"; do
        app="${b%%:*}"; name="${b##*:}"
        [[ -d "/Applications/$app" ]] && { echo "$name"; return 0; }
      done
      ;;
    Linux|*)
      for b in firefox chrome chromium edge brave; do
        command -v "$b" >/dev/null 2>&1 && { echo "$b"; return 0; }
      done
      ;;
  esac
  return 1
}

# 抖音 / 小红书需要登录态；其余平台免 cookie
EXTRA=()
case "$URL" in
  *douyin.com*|*v.douyin.com*|*xiaohongshu.com*|*xhslink.com*)
    if [[ -f "$CF" ]]; then
      EXTRA=(--cookies "$CF" -f "best[format_id!^=download_addr]/best")
    else
      B="$(detect_browser)" || true
      if [[ -n "$B" ]]; then
        EXTRA=(--cookies-from-browser "$B" -f "best[format_id!^=download_addr]/best")
      else
        echo "⚠️  抖音/小红书需要登录态：未找到浏览器，也无法读取 cookie 文件 $CF" >&2
        echo "    请在浏览器登录抖音/小红书后重试，或把 Netscape 格式 cookie 放到 $CF" >&2
        exit 1
      fi
    fi
    ;;
esac

if [[ ${#EXTRA[@]} -gt 0 ]]; then
  exec "$YTDLP" "${EXTRA[@]}" \
    --socket-timeout 30 \
    --no-check-certificates \
    --no-playlist \
    -o "$OUT/%(title).60s [%(id)s].%(ext)s" \
    "$URL"
else
  exec "$YTDLP" \
    --socket-timeout 30 \
    --no-check-certificates \
    --no-playlist \
    -o "$OUT/%(title).60s [%(id)s].%(ext)s" \
    "$URL"
fi
