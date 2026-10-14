#!/usr/bin/env python3
"""Collect real high-performing reference videos for each niche.

Pulls live public metadata (views, likes, comments, duration, date, channel)
with yt-dlp and writes:
    research/references_<stamp>.json   raw evidence
    docs/REFERENCE_VIDEOS.md           a readable table for K

These are references only: links to study patterns. No footage, music or script
is ever downloaded or reused.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
YTDLP = os.path.expanduser("~/.local/bin/yt-dlp")

NICHES = {
    "Scary stories (animated)": [
        "scary story animated short film",
        "true horror stories animated",
        "creepy stories animated",
    ],
    "Space facts": [
        "space facts shorts",
        "universe facts shorts",
        "mind blowing space facts",
    ],
    "History facts": [
        "history facts shorts",
        "historical facts you didnt know",
        "history facts that sound fake",
    ],
    "What-if / physics": [
        "what if you fell through earth",
        "what if scenario animated",
        "what if explained universe",
    ],
    "Unsolved mysteries": [
        "unsolved mystery shorts",
        "unexplained mysteries",
        "cold case mystery",
    ],
    "AI animated story": [
        "ai animated short story",
        "animated short story",
        "ai generated story video",
    ],
}

# Vertical short-form specifically: yt-dlp can filter to Shorts-length uploads.
SHORTS_NICHES = {
    "Shorts - horror/scary": ["scary story #shorts", "horror story shorts"],
    "Shorts - space": ["space facts #shorts", "universe shorts"],
    "Shorts - history": ["history facts #shorts", "history shorts"],
    "Shorts - what-if": ["what if #shorts", "what if you shorts"],
    "Shorts - mystery": ["mystery facts #shorts", "unsolved mystery #shorts"],
}


def search(query: str, limit: int) -> list[dict]:
    cmd = [YTDLP, "--dump-json", "--no-warnings", "--ignore-errors",
           f"ytsearch{limit}:{query}"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    except subprocess.TimeoutExpired:
        return []
    out = []
    for line in r.stdout.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            d = json.loads(line)
        except Exception:  # noqa: BLE001
            continue
        out.append({
            "id": d.get("id"),
            "title": d.get("title"),
            "channel": d.get("channel") or d.get("uploader"),
            "url": d.get("webpage_url") or f"https://www.youtube.com/watch?v={d.get('id')}",
            "views": d.get("view_count"),
            "likes": d.get("like_count"),
            "comments": d.get("comment_count"),
            "duration_s": d.get("duration"),
            "upload_date": d.get("upload_date"),
            "vertical": bool(d.get("width") and d.get("height")
                             and d["height"] > d["width"]),
        })
    return out


def fmt(n) -> str:
    if n is None:
        return "-"
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-query", type=int, default=5)
    ap.add_argument("--niche", default=None, help="only this niche key")
    ap.add_argument("--shorts", action="store_true",
                    help="collect vertical short-form references only")
    ap.add_argument("--long", action="store_true",
                    help="collect long-form references only")
    args = ap.parse_args()

    niches = {**NICHES, **SHORTS_NICHES}
    if args.shorts:
        niches = SHORTS_NICHES
    elif args.long:
        niches = NICHES
    elif args.niche:
        pool = {**NICHES, **SHORTS_NICHES}
        niches = {k: v for k, v in pool.items() if args.niche.lower() in k.lower()}

    result = {}
    for niche, queries in niches.items():
        seen = {}
        for q in queries:
            for v in search(q, args.per_query):
                if v["id"] and v["id"] not in seen:
                    seen[v["id"]] = v
        items = sorted(seen.values(), key=lambda x: (x["views"] or 0), reverse=True)
        result[niche] = items
        print(f"[ref] {niche}: {len(items)} videos", file=sys.stderr)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    raw_path = os.path.join(ROOT, "research", f"references_{stamp}.json")
    os.makedirs(os.path.dirname(raw_path), exist_ok=True)
    with open(raw_path, "w") as f:
        json.dump({
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "method": "yt-dlp ytsearch (public metadata only)",
            "niches": result,
        }, f, indent=2, ensure_ascii=False)

    lines = [
        "# Reference Videos — real high-performing examples",
        "",
        f"Collected: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "Live public YouTube metadata pulled with yt-dlp. These are **references for study only** —",
        "no footage, music or script from these videos is downloaded or reused.",
        "Raw evidence: `research/" + os.path.basename(raw_path) + "`",
        "",
        "> Views are a reach signal, not proof of revenue.",
        "",
    ]
    for niche, items in result.items():
        lines.append(f"## {niche}")
        lines.append("")
        if not items:
            lines.append("_No results returned._")
            lines.append("")
            continue
        lines.append("| Views | Likes | Comments | Len | Date | Title | Channel | Link |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for v in items[:8]:
            dur = f"{v['duration_s']}s" if v["duration_s"] else "-"
            date = v["upload_date"] or "-"
            if len(date) == 8:
                date = f"{date[:4]}-{date[4:6]}-{date[6:]}"
            title = (v["title"] or "").replace("|", "/")[:60]
            ch = (v["channel"] or "").replace("|", "/")[:22]
            lines.append(
                f"| {fmt(v['views'])} | {fmt(v['likes'])} | {fmt(v['comments'])} | {dur} "
                f"| {date} | {title} | {ch} | [watch]({v['url']}) |")
        lines.append("")

    md_path = os.path.join(ROOT, "docs", "REFERENCE_VIDEOS.md")
    with open(md_path, "w") as f:
        f.write("\n".join(lines))

    print(json.dumps({"raw": raw_path, "markdown": md_path,
                      "total": sum(len(v) for v in result.values())}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
