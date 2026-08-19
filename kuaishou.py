#!/usr/bin/env python3
# kuaishou.py —— 快手视频直链解析（零依赖，仅标准库）
#
# yt-dlp 原生不支持快手，这里用快手 web GraphQL 接口拿直链，再交给 yt-dlp 下载/合并。
# 公开视频通常可免登录；若触发反爬验证码（result 400002），自动复用 yt-dlp 从本地
# 已登录浏览器（edge/chrome…）导出的登录态 cookie 重试。也支持手动放置
# ~/.kuaishou_cookies.txt（Netscape 格式）或设 KUAISHOU_COOKIE 环境变量。
#
# 用法: python3 kuaishou.py "<快手链接>"
# 输出: 第 1 行 = 标题（已清洗）；第 2 行 = 媒体直链（mp4）
import os
import re
import sys
import json
import time
import random
import string
import subprocess
import tempfile
from urllib import request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
GRAPHQL = "https://www.kuaishou.com/graphql"

DETAIL_QUERY = """
query visionVideoDetail($photoId: String, $page: String) {
  visionVideoDetail(photoId: $photoId, page: $page) {
    status
    photo {
      caption
      photoUrl
      photoH265Url
      videoResource
    }
  }
}
"""

# 浏览器探测顺序：海荣的快手登录态在 Edge，故 Edge 优先
BROWSERS = ("edge", "chrome", "chromium", "brave")


def photo_id(url):
    if "v.kuaishou.com" in url:
        url = _resolve(url)
    for pat in (r"/short-video/([A-Za-z0-9_\-]+)",
                r"/f/([A-Za-z0-9_\-]+)",
                r"[?&]photoId=([A-Za-z0-9_\-]+)"):
        m = re.search(pat, url)
        if m:
            return m.group(1)
    return None


def _resolve(url):
    req = request.Request(url, headers={"User-Agent": UA})
    try:
        with request.urlopen(req, timeout=20) as r:
            return r.geturl()
    except Exception:
        return url


def _gen_did():
    return "web_" + "".join(random.choice(string.hexdigits.lower()) for _ in range(32))


def _load_cookie():
    raw = os.environ.get("KUAISHOU_COOKIE")
    if raw:
        return raw.strip()
    p = os.environ.get("KUAISHOU_COOKIE_FILE") or os.path.expanduser("~/.kuaishou_cookies.txt")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return f.read().strip()
    return None


def _browser_cookie_string():
    """用 yt-dlp 从本地浏览器导出 kuaishou 登录态 cookie，拼成字符串返回；无则 None。"""
    for b in BROWSERS:
        try:
            fd, path = tempfile.mkstemp(suffix=".txt")
            os.close(fd)
            os.unlink(path)  # 关键：文件必须不存在，yt-dlp 才会把浏览器 cookie 导出并创建它
            # yt-dlp 对快手本身不支持会报错，但在加载浏览器 cookie 阶段已把它导出到文件
            subprocess.run(
                ["yt-dlp", "--cookies-from-browser", b, "--cookies", path,
                 "https://www.kuaishou.com/short-video/0"],
                capture_output=True, timeout=90)
            cookies = []
            with open(path, encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    parts = line.split("\t")
                    if len(parts) >= 7 and "kuaishou.com" in parts[0]:
                        cookies.append("%s=%s" % (parts[5], parts[6]))
            os.unlink(path)
            if cookies:
                return "; ".join(cookies)
        except Exception:
            continue
    return None


def fetch(pid, cookie=None):
    if cookie is None:
        cookie = _load_cookie() or "did=%s; didv=%s; kpf=PC_WEB; clientid=3; kpn=KUAISHOU_VISION" % (
            _gen_did(), str(int(time.time() * 1000)))
    payload = json.dumps({
        "operationName": "visionVideoDetail",
        "variables": {"photoId": pid, "page": "detail"},
        "query": DETAIL_QUERY,
    }).encode("utf-8")
    req = request.Request(GRAPHQL, data=payload, method="POST")
    req.add_header("User-Agent", UA)
    req.add_header("Content-Type", "application/json")
    req.add_header("Origin", "https://www.kuaishou.com")
    req.add_header("Referer", "https://www.kuaishou.com/short-video/%s" % pid)
    req.add_header("Cookie", cookie)
    req.add_header("Accept", "application/json")
    with request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def pick_media(photo):
    cands = []  # (url, quality)
    vr = photo.get("videoResource") or {}
    for codec in ("h264", "h265"):
        for s in (vr.get(codec) or {}).get("adaptationSet", []) or []:
            for r in s.get("representation", []) or []:
                u = r.get("url")
                if not u:
                    continue
                try:
                    q = float(r.get("quality") or 0)
                except (TypeError, ValueError):
                    q = 0
                cands.append((u, q))
    # 兜底：封面/直链字段（无质量信息时权重最低）
    for key in ("photoH265Url", "photoUrl"):
        if photo.get(key):
            cands.append((photo[key], -1))
    if not cands:
        return None
    mp4 = [c for c in cands if not c[0].endswith(".m3u8")]
    pool = mp4 or cands
    pool.sort(key=lambda x: x[1], reverse=True)
    return pool[0][0]


def main():
    if len(sys.argv) < 2:
        print("用法: kuaishou.py <快手链接>", file=sys.stderr)
        return 2
    url = sys.argv[1]
    pid = photo_id(url)
    if not pid:
        print("无法从链接解析快手视频ID: %s" % url, file=sys.stderr)
        return 3
    # 1) 先试（免登录或手动 cookie）
    resp = fetch(pid)
    photo = (resp.get("data") or {}).get("visionVideoDetail", {}).get("photo")
    # 2) 若被反爬拦截（空 / 验证码），复用浏览器登录态重试
    if not photo:
        bcookie = _browser_cookie_string()
        if bcookie:
            try:
                resp = fetch(pid, cookie=bcookie)
                photo = (resp.get("data") or {}).get("visionVideoDetail", {}).get("photo")
            except Exception:
                photo = None
    if not photo:
        print("快手返回为空（视频可能已删除/设为私密，或浏览器无登录态）", file=sys.stderr)
        print("若仍失败，请把浏览器里快手 Cookie 写入 ~/.kuaishou_cookies.txt 后重试。", file=sys.stderr)
        return 5
    media = pick_media(photo)
    if not media:
        print("未找到可下载的媒体直链", file=sys.stderr)
        return 6
    title = (photo.get("caption") or "kuaishou").replace("\n", " ").strip()[:80]
    title = re.sub(r'[\\/:*?"<>|]', "_", title) or "kuaishou"
    print(title)
    print(media)
    return 0


if __name__ == "__main__":
    sys.exit(main())
