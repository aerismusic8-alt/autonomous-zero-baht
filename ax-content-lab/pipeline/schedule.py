#!/usr/bin/env python3
"""Scheduled multi-platform posting.

Picks the next queued QC_PASS item and publishes it to every ready platform at
the configured slot times. Idempotent: the (slug, platform) pair is unique in the
database, so a re-run never double-posts.

Slots are local times (default Asia/Bangkok). Run this from cron/automation; it
posts at most one item per platform per invocation.

Usage:
    python3 pipeline/schedule.py --show                 # current plan
    python3 pipeline/schedule.py --tick                 # post if a slot is due now
    python3 pipeline/schedule.py --tick --force         # post regardless of time
    python3 pipeline/schedule.py --tick --dry-run       # show what would post
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import platforms  # noqa: E402
import store  # noqa: E402
from multipost import load_items, UPLOADERS, _record  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Posting slots, local time. Four a day keeps YouTube inside its 6/day quota and
# spaces posts so the algorithms do not see a burst.
SLOTS = ["09:00", "13:00", "18:00", "21:00"]
TZ_OFFSET_HOURS = 7  # Asia/Bangkok (UTC+7), no DST

# How many items to publish per slot, per platform.
PER_SLOT = 1


def local_now() -> datetime:
    return datetime.now(timezone.utc) + timedelta(hours=TZ_OFFSET_HOURS)


def due_slots(now: datetime, window_min: int = 30) -> list[str]:
    """Slots whose time has passed within the last `window_min` minutes."""
    out = []
    for s in SLOTS:
        hh, mm = (int(x) for x in s.split(":"))
        slot_dt = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
        delta = (now - slot_dt).total_seconds() / 60
        if 0 <= delta <= window_min:
            out.append(s)
    return out


def published_pairs() -> set[tuple[str, str]]:
    con = store.connect()
    rows = con.execute("SELECT slug, platform FROM publications").fetchall()
    return {(r["slug"], r["platform"]) for r in rows}


def queue(platform: str) -> list[dict]:
    done = published_pairs()
    items = []
    for it in load_items():
        if (it["slug"], platform) not in done:
            items.append(it)
    return items


def plan() -> dict:
    ready = platforms.ready_platforms()
    out = {"slots_local": SLOTS, "timezone": f"UTC+{TZ_OFFSET_HOURS}",
           "ready_platforms": ready, "blocked": {}, "next": []}
    for k, v in platforms.status().items():
        if not v["ready"]:
            out["blocked"][k] = {"missing": v["missing"], "needs": v["needs_from_k"]}
    for p in ready:
        q = queue(p)
        out["next"].append({"platform": p, "queued": len(q),
                            "next_slug": q[0]["slug"] if q else None})
    out["queued_total"] = sum(len(queue(p)) for p in ready)
    return out


def tick(force: bool = False, dry_run: bool = False) -> dict:
    now = local_now()
    slots = due_slots(now)
    if not slots and not force:
        return {"posted": 0, "reason": f"no slot due at {now:%H:%M} local",
                "slots": SLOTS}
    ready = platforms.ready_platforms()
    if not ready:
        return {"posted": 0, "reason": "no platform has credentials yet",
                "blocked": list(platforms.status().keys())}

    results = []
    for p in ready:
        q = queue(p)
        if not q:
            results.append({"platform": p, "status": "EMPTY_QUEUE"})
            continue
        for item in q[:PER_SLOT]:
            if dry_run:
                results.append({"platform": p, "slug": item["slug"],
                                "status": "DRY_RUN"})
                continue
            r = UPLOADERS[p](item) if p != "youtube" else UPLOADERS[p](item, "public")
            st = _record(item["slug"], p, r.get("url"), r.get("id"),
                         r.get("ok", False), r.get("note", ""))
            results.append({"platform": p, "slug": item["slug"], "status": st,
                            "url": r.get("url"), "note": r.get("note")})
    posted = sum(1 for r in results if r["status"] == "PUBLISHED")
    return {"at_local": now.strftime("%Y-%m-%d %H:%M"), "slots_due": slots,
            "posted": posted, "results": results}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--show", action="store_true")
    ap.add_argument("--tick", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.show or not args.tick:
        print(json.dumps(plan(), indent=2, ensure_ascii=False))
        return 0
    print(json.dumps(tick(force=args.force, dry_run=args.dry_run),
                     indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
