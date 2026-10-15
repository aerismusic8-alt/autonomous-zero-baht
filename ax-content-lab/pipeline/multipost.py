#!/usr/bin/env python3
"""Multi-platform uploader for YouTube, TikTok, Facebook Reels, Instagram Reels.

Hard rule: a post is recorded as PUBLISHED only when the platform returns a real
id/url that we store. If a credential is missing, the result is BLOCKED with the
exact file K must provide - never a fake success.

Usage:
    python3 pipeline/multipost.py --status          # what is ready, what is blocked
    python3 pipeline/multipost.py --dry-run         # validate every package
    python3 pipeline/multipost.py --platform youtube --all
    python3 pipeline/multipost.py --all             # every ready platform
"""
from __future__ import annotations
import toolchain  # noqa: F401  (ensures ffmpeg/ffprobe on PATH)

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import platforms  # noqa: E402
import store  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, "content")


def load_items(only_slug: str | None = None) -> list[dict]:
    items = []
    for d in sorted(os.listdir(CONTENT)):
        wd = os.path.join(CONTENT, d)
        mp4 = os.path.join(wd, "final.mp4")
        meta_p = os.path.join(wd, "metadata.json")
        qc_p = os.path.join(wd, "qc_report.json")
        if not (os.path.isfile(mp4) and os.path.isfile(meta_p)):
            continue
        if only_slug and only_slug not in d:
            continue
        qc = {}
        if os.path.isfile(qc_p):
            with open(qc_p) as f:
                qc = json.load(f)
        if qc.get("status") != "PASS":
            continue
        with open(meta_p) as f:
            meta = json.load(f)
        items.append({"slug": d, "dir": wd, "mp4": mp4, "meta": meta, "qc": qc})
    return items


def _record(slug: str, platform: str, url: str | None, pid: str | None,
            ok: bool, note: str):
    con = store.connect()
    if ok and (url or pid):
        store.record_publication(con, slug, platform, url or "", pid or "",
                                 {"note": note, "at": store.now()})
        status = "PUBLISHED"
    else:
        status = "BLOCKED"
        store.log_decision(con, f"publish_{platform}",
                           f"{slug}: {note}", json.dumps({"platform": platform}))
    return status


# --------------------------------------------------------------------------- #
# Packaging helpers — metadata.json keeps title/description/tags at the top
# level (see produce.py); packaging is derived from those.
# --------------------------------------------------------------------------- #
def _packaging(meta: dict) -> dict:
    pkg = meta.get("packaging") or {}
    return {
        "title": (pkg.get("title") or meta.get("title") or "").strip(),
        "description": (pkg.get("description") or meta.get("description") or "").strip(),
        "tags": pkg.get("tags") or meta.get("tags") or [],
        "hashtags": pkg.get("hashtags") or meta.get("hashtags") or [],
    }


def _shorts_title(title: str) -> str:
    """YouTube Shorts ranking reads '#Shorts' from the title or description."""
    title = title.strip()
    if "#shorts" in title.lower():
        return title[:100]
    return (title + " #Shorts")[:100]


def _shorts_description(description: str) -> str:
    desc = description.rstrip()
    if "#shorts" not in desc.lower():
        desc = (desc + "\n\n#Shorts").strip()
    return desc[:4900]


# --------------------------------------------------------------------------- #
# YouTube
# --------------------------------------------------------------------------- #
def upload_youtube(item: dict, privacy: str = "public") -> dict:
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
    except ImportError as e:
        return {"ok": False, "note": f"google client libs missing: {e}"}

    scopes = ["https://www.googleapis.com/auth/youtube.upload"]
    tok = platforms.path("youtube_token.json")
    cli = platforms.path("youtube_client_secret.json")
    if not os.path.isfile(cli):
        return {"ok": False, "note": f"BLOCKED: missing {cli}"}

    creds = None
    if os.path.isfile(tok):
        creds = Credentials.from_authorized_user_file(tok, scopes)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(cli, scopes)
        creds = flow.run_local_server(port=0)  # needs a human browser once
        with open(tok, "w") as f:
            f.write(creds.to_json())

    yt = build("youtube", "v3", credentials=creds)
    pkg = _packaging(item["meta"])
    title = _shorts_title(pkg["title"])
    body = {
        "snippet": {
            "title": title,
            "description": _shorts_description(pkg["description"]),
            "tags": pkg["tags"][:500],
            "categoryId": "24",
        },
        "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": False},
    }
    media = MediaFileUpload(item["mp4"], mimetype="video/mp4", resumable=True)
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    resp = None
    while resp is None:
        _, resp = req.next_chunk()
    vid = resp.get("id")
    if not vid:
        return {"ok": False, "note": "upload returned no video id"}
    return {"ok": True, "url": f"https://youtube.com/shorts/{vid}", "id": vid,
            "note": "youtube videos.insert ok"}


# --------------------------------------------------------------------------- #
# TikTok
# --------------------------------------------------------------------------- #
def upload_tiktok(item: dict) -> dict:
    tok = platforms.load("tiktok_token.json")
    if not tok or not tok.get("access_token"):
        return {"ok": False, "note": f"BLOCKED: missing {platforms.path('tiktok_token.json')}"}
    try:
        import requests
    except ImportError:
        return {"ok": False, "note": "requests missing"}

    size = os.path.getsize(item["mp4"])
    init = requests.post(
        "https://open.tiktokapis.com/v2/post/publish/inbox/video/init/",
        headers={"Authorization": f"Bearer {tok['access_token']}",
                 "Content-Type": "application/json"},
        json={"source_info": {"source": "FILE_UPLOAD", "video_size": size,
                              "chunk_size": size, "total_chunk_count": 1}},
        timeout=60)
    if init.status_code != 200:
        return {"ok": False, "note": f"tiktok init HTTP {init.status_code}: {init.text[:200]}"}
    data = init.json().get("data", {})
    url = data.get("upload_url")
    pub_id = data.get("publish_id")
    if not url:
        return {"ok": False, "note": f"tiktok init gave no upload_url: {init.text[:200]}"}

    with open(item["mp4"], "rb") as f:
        body = f.read()
    put = requests.put(url, headers={"Content-Type": "video/mp4",
                                     "Content-Range": f"bytes 0-{size-1}/{size}",
                                     "Content-Length": str(size)},
                       data=body, timeout=300)
    if put.status_code not in (200, 201, 206):
        return {"ok": False, "note": f"tiktok upload HTTP {put.status_code}"}
    return {"ok": True, "url": f"https://www.tiktok.com/upload?publish_id={pub_id}",
            "id": pub_id, "note": "tiktok inbox upload ok (creator confirms in app)"}


# --------------------------------------------------------------------------- #
# Facebook Reels + Instagram Reels (Graph API)
# --------------------------------------------------------------------------- #
def upload_facebook(item: dict, privacy: str = "PUBLIC") -> dict:
    tok = platforms.load("meta_token.json")
    if not tok or not tok.get("access_token") or not tok.get("page_id"):
        return {"ok": False, "note": f"BLOCKED: missing {platforms.path('meta_token.json')}"}
    try:
        import requests
    except ImportError:
        return {"ok": False, "note": "requests missing"}

    base = "https://graph.facebook.com/v21.0"
    page, at = tok["page_id"], tok["access_token"]
    size = os.path.getsize(item["mp4"])
    start = requests.post(f"{base}/{page}/video_reels",
                          data={"upload_phase": "start", "access_token": at},
                          timeout=60)
    if start.status_code != 200:
        return {"ok": False, "note": f"fb start HTTP {start.status_code}: {start.text[:200]}"}
    vid = start.json().get("video_id")
    upload_url = start.json().get("upload_url")
    if not (vid and upload_url):
        return {"ok": False, "note": f"fb start gave no upload url: {start.text[:200]}"}

    with open(item["mp4"], "rb") as f:
        body = f.read()
    up = requests.post(upload_url, headers={
        "Authorization": f"OAuth {at}", "offset": "0", "file_size": str(size)},
        data=body, timeout=300)
    if up.status_code != 200:
        return {"ok": False, "note": f"fb upload HTTP {up.status_code}: {up.text[:200]}"}

    fin = requests.post(f"{base}/{page}/video_reels",
                        data={"upload_phase": "finish", "video_id": vid,
                              "video_state": "PUBLISHED", "access_token": at},
                        timeout=60)
    if fin.status_code != 200:
        return {"ok": False, "note": f"fb finish HTTP {fin.status_code}: {fin.text[:200]}"}
    return {"ok": True, "url": f"https://www.facebook.com/reel/{vid}", "id": vid,
            "note": "fb reels published"}


def upload_instagram(item: dict) -> dict:
    tok = platforms.load("meta_token.json")
    if not tok or not tok.get("access_token") or not tok.get("ig_user_id"):
        return {"ok": False, "note": f"BLOCKED: missing ig_user_id in {platforms.path('meta_token.json')}"}
    try:
        import requests
    except ImportError:
        return {"ok": False, "note": "requests missing"}

    base = "https://graph.facebook.com/v21.0"
    ig, at = tok["ig_user_id"], tok["access_token"]
    pkg = _packaging(item["meta"])

    # Instagram pulls the video from a public URL, so it must be hosted first.
    public_base = os.environ.get("AX_PUBLIC_BASE", "").rstrip("/")
    if not public_base:
        return {"ok": False, "note": "BLOCKED: set AX_PUBLIC_BASE to a public URL "
                                     "where final.mp4 is reachable, then retry"}
    video_url = f"{public_base}/media/{item['slug']}/final.mp4"

    caption = pkg["description"]
    if pkg["hashtags"]:
        tags = pkg["hashtags"] if isinstance(pkg["hashtags"], str) else " ".join(pkg["hashtags"])
        caption = f"{caption}\n\n{tags}".strip()
    create = requests.post(f"{base}/{ig}/media", data={
        "media_type": "REELS", "video_url": video_url,
        "caption": caption[:2100],
        "access_token": at}, timeout=120)
    if create.status_code != 200:
        return {"ok": False, "note": f"ig create HTTP {create.status_code}: {create.text[:200]}"}
    container = create.json().get("id")

    # Reels need processing time before publish.
    for _ in range(30):
        st = requests.get(f"{base}/{container}", params={
            "fields": "status_code", "access_token": at}, timeout=30)
        code = st.json().get("status_code")
        if code == "FINISHED":
            break
        if code == "ERROR":
            return {"ok": False, "note": "ig container processing error"}
        time.sleep(10)

    pub = requests.post(f"{base}/{ig}/media_publish", data={
        "creation_id": container, "access_token": at}, timeout=120)
    if pub.status_code != 200:
        return {"ok": False, "note": f"ig publish HTTP {pub.status_code}: {pub.text[:200]}"}
    mid = pub.json().get("id")
    return {"ok": True, "url": f"https://www.instagram.com/reel/{mid}", "id": mid,
            "note": "ig reels published"}


UPLOADERS = {
    "youtube": upload_youtube,
    "tiktok": upload_tiktok,
    "facebook": upload_facebook,
    "instagram": upload_instagram,
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--platform", default=None)
    ap.add_argument("--slug", default=None)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--privacy", default="public")
    args = ap.parse_args()

    if args.status:
        print(json.dumps(platforms.status(), indent=2, ensure_ascii=False))
        return 0

    items = load_items(args.slug)
    if not items:
        print("no QC_PASS items found")
        return 1

    targets = ([args.platform] if args.platform
               else (platforms.ready_platforms() if args.all else []))
    if not targets:
        print(json.dumps({"error": "no ready platform; run --status",
                          "ready": platforms.ready_platforms()}, indent=2))
        return 3

    results = []
    for it in items:
        for p in targets:
            if args.dry_run:
                pkg = _packaging(it["meta"])
                entry = {
                    "slug": it["slug"], "platform": p, "status": "DRY_RUN",
                    "size_mb": round(os.path.getsize(it["mp4"]) / 1e6, 2),
                    "resolution": it["meta"].get("resolution"),
                    "duration_s": it["meta"].get("duration_seconds"),
                    "title": _shorts_title(pkg["title"]) if p == "youtube" else pkg["title"],
                    "description": pkg["description"][:300],
                    "tags": pkg["tags"][:10],
                }
                creds_ok = platforms.status().get(p, {}).get("ready")
                entry["credentials"] = "ready" if creds_ok else "BLOCKED"
                if not creds_ok:
                    entry["blocked_on"] = platforms.status()[p]["missing"]
                results.append(entry)
                continue
            r = UPLOADERS[p](it, args.privacy) if p == "youtube" else UPLOADERS[p](it)
            status = _record(it["slug"], p, r.get("url"), r.get("id"),
                             r.get("ok", False), r.get("note", ""))
            results.append({"slug": it["slug"], "platform": p, "status": status,
                            "url": r.get("url"), "note": r.get("note")})

    print(json.dumps({"items": len(items), "targets": targets, "results": results},
                     indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
