#!/usr/bin/env python3
"""Batch production runner: produce all specs in content/specs in parallel."""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import produce  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_one(spec_path: str, force: bool = False) -> dict:
    t0 = time.time()
    try:
        res = produce.build(spec_path, force=force)
        skipped = res.get("skipped", False)
        return {
            "spec": os.path.basename(spec_path),
            "slug": res["metadata"]["slug"],
            "qc_status": res["qc"]["status"],
            "qc": f"{res['qc']['passed']}/{res['qc']['total']}",
            "duration": res["metadata"]["duration_seconds"],
            "seconds": round(time.time() - t0, 1),
            "skipped": skipped,
            "ok": True,
        }
    except Exception as e:  # noqa: BLE001
        return {"spec": os.path.basename(spec_path), "ok": False,
                "error": f"{type(e).__name__}: {e}", "seconds": round(time.time() - t0, 1)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--pattern", default="spec_*.json")
    ap.add_argument("--only", nargs="*", default=None, help="slug substrings to include")
    ap.add_argument("--force", action="store_true", help="rebuild even if already produced")
    args = ap.parse_args()

    specs = sorted(glob.glob(os.path.join(ROOT, "content", "specs", args.pattern)))
    if args.only:
        specs = [s for s in specs if any(o in os.path.basename(s) for o in args.only)]
    if not specs:
        print("no specs matched", file=sys.stderr)
        return 1

    print(f"producing {len(specs)} piece(s) with {args.workers} workers", file=sys.stderr)
    results = []
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(run_one, s, args.force): s for s in specs}
        for fut in as_completed(futs):
            r = fut.result()
            results.append(r)
            flag = "OK " if r.get("ok") else "ERR"
            print(f"[{flag}] {r.get('slug', r['spec'])} qc={r.get('qc_status','-')} "
                  f"{r.get('qc','')} {r.get('seconds')}s {r.get('error','')}", file=sys.stderr)

    ok = [r for r in results if r.get("ok")]
    passed = [r for r in ok if r.get("qc_status") == "PASS"]
    summary = {
        "produced": len(ok),
        "qc_pass": len(passed),
        "failed": [r for r in results if not r.get("ok")],
        "results": sorted(results, key=lambda r: r["spec"]),
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    out = os.path.join(ROOT, "content", "batch_summary.json")
    with open(out, "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(json.dumps({k: summary[k] for k in ("produced", "qc_pass")}, indent=2))
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
