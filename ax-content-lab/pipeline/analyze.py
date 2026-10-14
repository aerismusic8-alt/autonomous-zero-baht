#!/usr/bin/env python3
"""Analyze collected research snapshots -> patterns table (markdown)."""
from __future__ import annotations

import glob
import json
import os
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESEARCH_DIR = os.path.join(ROOT, "research")


def load_all() -> list[dict]:
    snaps = []
    for p in sorted(glob.glob(os.path.join(RESEARCH_DIR, "*.json"))):
        with open(p) as f:
            s = json.load(f)
        s["_file"] = os.path.basename(p)
        snaps.append(s)
    return snaps


def fmt(n):
    return f"{n:,}" if isinstance(n, (int, float)) else "-"


def main() -> int:
    snaps = load_all()
    if not snaps:
        print("no research snapshots found", file=sys.stderr)
        return 1

    print("# Market Research Analysis\n")
    for s in snaps:
        print(f"## Snapshot: {s['_file']}")
        print(f"Collected: {s['collected_at']}  |  Method: {s['method']}\n")
        print("| Query | N | Median views | Max views | Median dur(s) | Shorts(<60s) |")
        print("|---|---|---|---|---|---|")
        for q, items in s["queries"].items():
            vc = [i["view_count"] for i in items if i.get("view_count")]
            durs = [i["duration"] for i in items if i.get("duration")]
            short = sum(1 for d in durs if d and d < 60)
            med = fmt(int(statistics.median(vc))) if vc else "-"
            mx = fmt(max(vc)) if vc else "-"
            md = f"{int(statistics.median(durs))}" if durs else "-"
            print(f"| {q} | {len(items)} | {med} | {mx} | {md} | {short}/{len(durs)} |")
        print()

        # recurring title patterns
        print("Top performers (view count):")
        all_items = [i for items in s["queries"].values() for i in items if i.get("view_count")]
        for i in sorted(all_items, key=lambda x: -x["view_count"])[:12]:
            d = i.get("duration")
            print(f"- {fmt(i['view_count']):>12} | {int(d) if d else '?':>5}s | {i['channel']} | {i['title'][:80]}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
