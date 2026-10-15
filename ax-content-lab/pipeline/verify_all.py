#!/usr/bin/env python3
"""Independently verify every produced video against the delivery spec.

Reads the actual files (not the QC self-report) and checks:
  - container/streams: H.264 video + AAC audio
  - resolution 1080x1920 (vertical)
  - duration 8-300 s (Shorts-eligible)
  - file is non-trivial (> 500 KB)

Prints a summary and exits non-zero if anything fails.
"""
from __future__ import annotations
import toolchain  # noqa: F401  (ensures ffmpeg/ffprobe on PATH)

import glob
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def probe(path: str) -> dict:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format",
         "-of", "json", path], capture_output=True, text=True)
    return json.loads(r.stdout or "{}")


def main() -> int:
    files = sorted(glob.glob(os.path.join(ROOT, "content", "*", "final.mp4")))
    rows, bad = [], []
    for f in files:
        d = probe(f)
        v = next((s for s in d.get("streams", []) if s.get("codec_type") == "video"), {})
        a = next((s for s in d.get("streams", []) if s.get("codec_type") == "audio"), {})
        dur = float(d.get("format", {}).get("duration", 0) or 0)
        size = os.path.getsize(f)
        checks = {
            "v_codec": v.get("codec_name") == "h264",
            "a_codec": a.get("codec_name") == "aac",
            "vertical": (v.get("width"), v.get("height")) == (1080, 1920),
            "duration": 8 <= dur <= 300,
            "size": size > 500_000,
            "has_audio": bool(a),
        }
        row = {"file": os.path.basename(os.path.dirname(f)),
               "dur": round(dur, 1), "size_kb": round(size / 1024),
               "fps": v.get("r_frame_rate"), "ok": all(checks.values())}
        if not row["ok"]:
            row["failed"] = [k for k, ok in checks.items() if not ok]
            bad.append(row)
        rows.append(row)

    print(json.dumps({
        "total": len(rows),
        "spec_compliant": len(rows) - len(bad),
        "failures": bad,
        "durations_s": [r["dur"] for r in rows],
    }, indent=2))
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(main())
