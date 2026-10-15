#!/usr/bin/env python3
"""Write docs/VIDEO_GALLERY.md - a permanent, GitHub-rendered index of clips.

Uses absolute raw URLs on the public branch, so every clip is reachable without
the sandbox gallery being awake.
"""
from __future__ import annotations
import toolchain  # noqa: F401  (ensures ffmpeg/ffprobe on PATH)

import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "VIDEO_GALLERY.md")
GH = ("https://github.com/aerismusic8-alt/autonomous-zero-baht/blob/"
      "ax-content-lab/ax-content-lab/content")
RAW = ("https://raw.githubusercontent.com/aerismusic8-alt/autonomous-zero-baht/"
       "ax-content-lab/ax-content-lab/content")


def main() -> int:
    items = []
    for d in sorted(glob.glob(os.path.join(ROOT, "content", "*"))):
        mp = os.path.join(d, "metadata.json")
        vp = os.path.join(d, "final.mp4")
        qp = os.path.join(d, "qc_report.json")
        if not (os.path.isfile(mp) and os.path.isfile(vp)):
            continue
        meta = json.load(open(mp))
        qc = json.load(open(qp)) if os.path.isfile(qp) else {}
        items.append((meta.get("slug", ""), meta.get("series", ""),
                      meta.get("title", ""), meta.get("duration_seconds"),
                      qc.get("status", ""), qc.get("passed"), qc.get("total")))

    lines = [
        "# Video gallery",
        "",
        f"{len(items)} finished clips. Click the raw link to play or download - these",
        "are permanent and do not depend on the sandbox gallery.",
        "",
        "| # | Series | Title | Length | QC | Play |",
        "|---|---|---|---|---|---|",
    ]
    for n, (slug, series, title, dur, qcs, p, t) in enumerate(items, 1):
        lines.append(
            f"| {n} | {series} | {title} | {dur}s | {qcs} {p}/{t} | "
            f"[MP4]({RAW}/{slug}/final.mp4) |")
    lines += [
        "",
        "## Thumbnails",
        "",
        "Each folder under `content/<slug>/` also holds `thumbnail.png`, "
        "`metadata.json` and `qc_report.json`.",
        "",
    ]
    with open(OUT, "w") as f:
        f.write("\n".join(lines))
    print(json.dumps({"page": OUT, "videos": len(items)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
