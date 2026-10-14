#!/usr/bin/env python3
"""Analytics: pull real post-publish stats and feed strategy decisions.

Only pulls stats for publications that have a *verified* real platform ID.
Never invents numbers. If no publication exists yet, reports zero honestly.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import publisher  # noqa: E402
import store  # noqa: E402


def fetch_youtube_stats(video_ids: list[str]) -> dict:
    from googleapiclient.discovery import build
    creds = publisher.yt_credentials()
    yt = build("youtube", "v3", credentials=creds, cache_discovery=False)
    out = {}
    for i in range(0, len(video_ids), 50):
        chunk = video_ids[i:i + 50]
        resp = yt.videos().list(part="statistics,contentDetails,snippet",
                                id=",".join(chunk)).execute()
        for item in resp.get("items", []):
            s = item.get("statistics", {})
            out[item["id"]] = {
                "views": int(s.get("viewCount", 0)),
                "likes": int(s.get("likeCount", 0)),
                "comments": int(s.get("commentCount", 0)),
                "title": item["snippet"]["title"],
                "published_at": item["snippet"]["publishedAt"],
            }
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--platform", default="youtube")
    args = ap.parse_args()

    con = store.connect()
    rows = con.execute(
        "SELECT slug, platform, platform_id, published_at FROM publications "
        "WHERE platform=? AND platform_id IS NOT NULL", (args.platform,)).fetchall()

    if not rows:
        report = {
            "platform": args.platform,
            "publications": 0,
            "note": "No verified publication yet. Nothing to measure. "
                    "Publishing is BLOCKED on platform OAuth (see docs/PUBLISHING.md).",
            "content_ready_awaiting_publish": store.summary().get("by_status", {}).get("QC_PASS", 0),
        }
        print(json.dumps(report, indent=2))
        return 0

    ids = [r["platform_id"] for r in rows]
    stats = fetch_youtube_stats(ids)
    for r in rows:
        s = stats.get(r["platform_id"])
        if not s:
            continue
        store.record_metrics(con, r["slug"], args.platform,
                             s["views"], s["likes"], s["comments"], s)
    con.close()
    print(json.dumps({"platform": args.platform, "measured": len(stats)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
