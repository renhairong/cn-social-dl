#!/usr/bin/env python3
# kuaishou.py —— 快手视频直链解析（零依赖，仅标准库）
#
# yt-dlp 原生不支持快手，这里用快手 web GraphQL 接口拿直链，再交给 yt-dlp 下载/合并。
# 公开视频通常可免登录；若返回空（已删除/私密/需登录态），把浏览器里快手 Cookie
# 复制成字符串写入 ~/.kuaishou_cookies.txt（或设环境变量 KUAISHOU_COOKIE）即可。
#
# 用法: python3 kuaishou.py "<快手链接>"
# 输出: 第 1 行 = 标题（已清洗）；第 2 行 = 媒体直链（mp4 或 m3u8）
import os
import re
import sys
import json
import time
import random
import string
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
      manifest
      manifestH265
      videoResource { resourceList { url quality } }
    }
  }
}
"""


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


def fetch(pid):
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
    cands = []
    for key in ("photoUrl", "photoH265Url"):
        if photo.get(key):
            cands.append((photo[key], 0))
    vr = photo.get("videoResource") or {}
    for item in vr.get("resourceList") or []:
        u = item.get("url")
        if not u:
            continue
        try:
            q = int(item.get("quality") or 0)
        except (TypeError, ValueError):
            q = 0
        cands.append((u, q))
    direct = [(u, q) for u, q in cands if u and not u.endswith(".m3u8")]
    hls = [(u, q) for u, q in cands if u and u.endswith(".m3u8")]
    best = direct or hls
    if not best:
        return None
    best.sort(key=lambda x: x[1], reverse=True)
    return best[0][0]


def main():
    if len(sys.argv) < 2:
        print("用法: kuaishou.py <快手链接>", file=sys.stderr)
        return 2
    url = sys.argv[1]
    pid = photo_id(url)
    if not pid:
        print("无法从链接解析快手视频ID: %s" % url, file=sys.stderr)
        return 3
    try:
        resp = fetch(pid)
    except Exception as e:  # noqa: BLE001
        print("请求快手接口失败: %s" % e, file=sys.stderr)
        return 4
    photo = (resp.get("data") or {}).get("visionVideoDetail", {}).get("photo")
    if not photo:
        print("快手返回为空（视频可能已删除/设为私密，或需要登录态）", file=sys.stderr)
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
