#!/usr/bin/env python3
"""Market research collector.

Uses yt-dlp to gather *real* public metadata (titles, view counts, upload dates,
channels, durations) for search queries. Saves raw evidence to research/*.json.

This is read-only research: no media is downloaded, no content is republished.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESEARCH_DIR = os.path.join(ROOT, "research")
YTDLP = os.path.expanduser("~/.local/bin/yt-dlp")


def search(query: str, limit: int = 20) -> list[dict]:
    """Return flat metadata for the top `limit` results of a yt-dlp search."""
    cmd = [
        YTDLP, "--skip-download", "--dump-json", "--no-warnings", "--ignore-errors",
        "--flat-playlist", f"ytsearch{limit}:{query}",
    ]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    items = []
    for line in out.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        items.append({
            "id": d.get("id"),
            "title": d.get("title"),
            "channel": d.get("channel") or d.get("uploader"),
            "channel_id": d.get("channel_id") or d.get("uploader_id"),
            "view_count": d.get("view_count"),
            "duration": d.get("duration"),
            "timestamp": d.get("timestamp"),
            "upload_date": d.get("upload_date"),
            "url": d.get("url") or (f"https://www.youtube.com/watch?v={d.get('id')}" if d.get("id") else None),
        })
    return items


def enrich(items: list[dict], limit: int) -> list[dict]:
    """Fetch full metadata (view counts etc.) for the first `limit` items."""
    for it in items[:limit]:
        if not it.get("url"):
            continue
        cmd = [YTDLP, "--skip-download", "--dump-json", "--no-warnings", "--ignore-errors", it["url"]]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        try:
            d = json.loads(r.stdout.splitlines()[0])
        except (json.JSONDecodeError, IndexError):
            continue
        it["view_count"] = d.get("view_count", it.get("view_count"))
        it["duration"] = d.get("duration", it.get("duration"))
        it["channel"] = d.get("channel", it.get("channel"))
        it["upload_date"] = d.get("upload_date", it.get("upload_date"))
        it["like_count"] = d.get("like_count")
        it["comment_count"] = d.get("comment_count")
        it["tags"] = (d.get("tags") or [])[:20]
    return items


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--queries", nargs="+", required=True)
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--enrich", type=int, default=8, help="how many results to fetch full stats for")
    ap.add_argument("--label", default="research")
    args = ap.parse_args()

    os.makedirs(RESEARCH_DIR, exist_ok=True)
    snapshot = {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "method": "yt-dlp search + metadata (public YouTube data, read-only)",
        "queries": {},
    }
    for q in args.queries:
        print(f"[research] query: {q}", file=sys.stderr)
        items = enrich(search(q, args.limit), args.enrich)
        snapshot["queries"][q] = items
        top = sorted([i for i in items if i.get("view_count")], key=lambda x: -x["view_count"])[:5]
        for t in top:
            print(f"  {t['view_count']:>10,}  {t['title'][:70]}", file=sys.stderr)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = os.path.join(RESEARCH_DIR, f"{args.label}_{ts}.json")
    with open(path, "w") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
