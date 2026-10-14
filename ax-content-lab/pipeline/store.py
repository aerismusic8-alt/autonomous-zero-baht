#!/usr/bin/env python3
"""Content state store (SQLite) + lifecycle tracking.

Statuses follow the project's required vocabulary:
    ASSUMPTION / IN PROGRESS / PENDING VERIFICATION / VERIFIED / BLOCKED
plus a content lifecycle stage. Nothing is marked PUBLISHED without a real URL.
"""
from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT, "data", "lab.sqlite3")

SCHEMA = """
CREATE TABLE IF NOT EXISTS content (
    slug TEXT PRIMARY KEY,
    series TEXT,
    title TEXT,
    status TEXT NOT NULL,          -- lifecycle: PRODUCED|QC_PASS|QC_FAIL|QUEUED|PUBLISHED|BLOCKED
    verification TEXT NOT NULL,    -- ASSUMPTION|IN PROGRESS|PENDING VERIFICATION|VERIFIED|BLOCKED
    qc_passed INTEGER,
    qc_total INTEGER,
    duration REAL,
    work_dir TEXT,
    created_at TEXT,
    updated_at TEXT
);
CREATE TABLE IF NOT EXISTS publications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT NOT NULL,
    platform TEXT NOT NULL,
    url TEXT,
    platform_id TEXT,
    published_at TEXT,
    evidence TEXT,
    UNIQUE(slug, platform)
);
CREATE TABLE IF NOT EXISTS metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT NOT NULL,
    platform TEXT NOT NULL,
    captured_at TEXT,
    views INTEGER,
    likes INTEGER,
    comments INTEGER,
    raw TEXT
);
CREATE TABLE IF NOT EXISTS decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    at TEXT,
    kind TEXT,
    summary TEXT,
    detail TEXT
);
CREATE TABLE IF NOT EXISTS experiments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    hypothesis TEXT,
    variable TEXT,
    status TEXT,
    created_at TEXT,
    result TEXT
);
"""


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def connect() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    return con


def upsert_content(con, slug, series, title, status, verification, qc_passed,
                   qc_total, duration, work_dir):
    con.execute("""
        INSERT INTO content (slug, series, title, status, verification, qc_passed,
                             qc_total, duration, work_dir, created_at, updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(slug) DO UPDATE SET
            status=excluded.status, verification=excluded.verification,
            qc_passed=excluded.qc_passed, qc_total=excluded.qc_total,
            duration=excluded.duration, work_dir=excluded.work_dir,
            updated_at=excluded.updated_at
    """, (slug, series, title, status, verification, qc_passed, qc_total,
          duration, work_dir, now(), now()))
    con.commit()


def record_publication(con, slug, platform, url, platform_id, evidence):
    con.execute("""
        INSERT INTO publications (slug, platform, url, platform_id, published_at, evidence)
        VALUES (?,?,?,?,?,?)
        ON CONFLICT(slug, platform) DO UPDATE SET
            url=excluded.url, platform_id=excluded.platform_id,
            published_at=excluded.published_at, evidence=excluded.evidence
    """, (slug, platform, url, platform_id, now(), json.dumps(evidence)))
    con.commit()


def record_metrics(con, slug, platform, views, likes, comments, raw):
    con.execute("""
        INSERT INTO metrics (slug, platform, captured_at, views, likes, comments, raw)
        VALUES (?,?,?,?,?,?,?)
    """, (slug, platform, now(), views, likes, comments, json.dumps(raw)))
    con.commit()


def log_decision(con, kind, summary, detail=""):
    con.execute("INSERT INTO decisions (at, kind, summary, detail) VALUES (?,?,?,?)",
                (now(), kind, summary, detail))
    con.commit()


def sync_from_disk() -> dict:
    """Scan content/*/metadata.json + qc_report.json and refresh the DB."""
    con = connect()
    n = 0
    for entry in sorted(os.listdir(os.path.join(ROOT, "content"))):
        d = os.path.join(ROOT, "content", entry)
        mp = os.path.join(d, "metadata.json")
        qp = os.path.join(d, "qc_report.json")
        if not os.path.isfile(mp):
            continue
        meta = json.load(open(mp))
        qc = json.load(open(qp)) if os.path.isfile(qp) else {}
        status = "QC_PASS" if qc.get("status") == "PASS" else (
            "QC_FAIL" if qc else "PRODUCED")
        upsert_content(con, meta["slug"], meta.get("series", ""), meta.get("title", ""),
                       status, "PENDING VERIFICATION", qc.get("passed", 0),
                       qc.get("total", 0), meta.get("duration_seconds", 0.0), d)
        n += 1
    con.close()
    return {"synced": n, "db": DB_PATH}


def summary() -> dict:
    con = connect()
    rows = con.execute("SELECT status, COUNT(*) c FROM content GROUP BY status").fetchall()
    pubs = con.execute("SELECT platform, COUNT(*) c FROM publications WHERE url IS NOT NULL GROUP BY platform").fetchall()
    total = con.execute("SELECT COUNT(*) c FROM content").fetchone()["c"]
    con.close()
    return {
        "content_total": total,
        "by_status": {r["status"]: r["c"] for r in rows},
        "published": {r["platform"]: r["c"] for r in pubs},
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "sync":
        print(json.dumps(sync_from_disk(), indent=2))
    print(json.dumps(summary(), indent=2))
