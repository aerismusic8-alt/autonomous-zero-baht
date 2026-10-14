#!/usr/bin/env python3
"""Publishing layer.

Reality check (verified 2026-10-14):
  * YouTube / TikTok / Instagram / Facebook all require *user identity* to grant
    an upload token. There is no legitimate free anonymous upload path.
  * This module therefore implements the uploader and a strict dry-run mode.
    It NEVER claims a post succeeded unless the platform returns a real ID/URL.

Auth model:
  YouTube  -> OAuth 2.0 installed-app flow. Client secret file at
              $AX_YT_CLIENT_SECRET (default: secrets/youtube_client_secret.json).
              Token cached at $AX_YT_TOKEN (default: secrets/youtube_token.json).
  Others   -> see docs/PUBLISHING.md (Meta Graph API / TikTok Content API).

Usage:
    python3 pipeline/publisher.py --dry-run          # validate packages only
    python3 pipeline/publisher.py --slug 0001_...    # upload one item (needs auth)
    python3 pipeline/publisher.py --all              # upload every QC_PASS item
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import store  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
YT_CLIENT_SECRET = os.environ.get("AX_YT_CLIENT_SECRET",
                                  os.path.join(ROOT, "secrets", "youtube_client_secret.json"))
YT_TOKEN = os.environ.get("AX_YT_TOKEN",
                          os.path.join(ROOT, "secrets", "youtube_token.json"))
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def package_ready(work_dir: str) -> tuple[bool, list[str]]:
    problems = []
    for f in ("final.mp4", "thumbnail.png", "metadata.json", "qc_report.json"):
        if not os.path.isfile(os.path.join(work_dir, f)):
            problems.append(f"missing {f}")
    qc_path = os.path.join(work_dir, "qc_report.json")
    if os.path.isfile(qc_path):
        qc = json.load(open(qc_path))
        if qc.get("status") != "PASS":
            problems.append(f"qc status {qc.get('status')}")
    return (not problems), problems


def yt_credentials():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    creds = None
    if os.path.isfile(YT_TOKEN):
        creds = Credentials.from_authorized_user_file(YT_TOKEN, SCOPES)
    if creds and creds.valid:
        return creds
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(YT_TOKEN, "w") as f:
            f.write(creds.to_json())
        return creds
    if not os.path.isfile(YT_CLIENT_SECRET):
        raise SystemExit(
            f"BLOCKED: YouTube OAuth client secret not found at {YT_CLIENT_SECRET}.\n"
            "This step requires K (human) to create a Google Cloud OAuth client.\n"
            "See docs/PUBLISHING.md for the exact steps."
        )
    flow = InstalledAppFlow.from_client_secrets_file(YT_CLIENT_SECRET, SCOPES)
    creds = flow.run_local_server(port=0)
    os.makedirs(os.path.dirname(YT_TOKEN), exist_ok=True)
    with open(YT_TOKEN, "w") as f:
        f.write(creds.to_json())
    return creds


def upload_youtube(slug: str, work_dir: str, privacy: str = "private",
                   publish_at: str | None = None) -> dict:
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    meta = json.load(open(os.path.join(work_dir, "metadata.json")))
    creds = yt_credentials()
    yt = build("youtube", "v3", credentials=creds, cache_discovery=False)

    status = {"privacyStatus": privacy, "selfDeclaredMadeForKids": False}
    if publish_at:
        status["publishAt"] = publish_at
        status["privacyStatus"] = "private"

    body = {
        "snippet": {
            "title": meta["title"][:100],
            "description": meta["description"][:5000],
            "tags": meta.get("tags", [])[:500],
            "categoryId": "24",  # Entertainment
        },
        "status": status,
    }
    media = MediaFileUpload(os.path.join(work_dir, "final.mp4"),
                            mimetype="video/mp4", resumable=True)
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        _, response = req.next_chunk()

    vid = response["id"]
    # set thumbnail (best effort; channel must be verified for custom thumbnails)
    try:
        yt.thumbnails().set(videoId=vid,
                            media_body=MediaFileUpload(
                                os.path.join(work_dir, "thumbnail.png"),
                                mimetype="image/png")).execute()
        thumb = True
    except Exception as e:  # noqa: BLE001
        thumb = f"thumbnail_failed: {e}"

    # VERIFY the post exists via API before recording it
    check = yt.videos().list(part="id,snippet,status", id=vid).execute()
    if not check.get("items"):
        raise RuntimeError(f"upload returned id {vid} but verification lookup failed")

    return {
        "platform": "youtube",
        "platform_id": vid,
        "url": f"https://www.youtube.com/watch?v={vid}",
        "privacy": privacy,
        "thumbnail": thumb,
        "verified": True,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--privacy", default="private",
                    choices=["private", "unlisted", "public"])
    args = ap.parse_args()

    con = store.connect()
    if args.slug:
        slugs = [args.slug]
    else:
        rows = con.execute("SELECT slug, work_dir FROM content WHERE status='QC_PASS'").fetchall()
        slugs = [r["slug"] for r in rows]

    results = []
    for slug in slugs:
        row = con.execute("SELECT * FROM content WHERE slug=?", (slug,)).fetchone()
        if not row:
            results.append({"slug": slug, "ok": False, "error": "not in store"})
            continue
        ok, problems = package_ready(row["work_dir"])
        if not ok:
            results.append({"slug": slug, "ok": False, "error": "; ".join(problems)})
            continue
        if args.dry_run:
            results.append({"slug": slug, "ok": True, "dry_run": True,
                            "package": "ready"})
            continue
        try:
            r = upload_youtube(slug, row["work_dir"], args.privacy)
            store.record_publication(con, slug, "youtube", r["url"],
                                     r["platform_id"], r)
            con.execute("UPDATE content SET status='PUBLISHED', verification='VERIFIED', "
                        "updated_at=? WHERE slug=?", (store.now(), slug))
            con.commit()
            results.append({"slug": slug, "ok": True, **r})
        except SystemExit as e:
            results.append({"slug": slug, "ok": False, "blocked": str(e)})
        except Exception as e:  # noqa: BLE001
            results.append({"slug": slug, "ok": False,
                            "error": f"{type(e).__name__}: {e}"})

    print(json.dumps({"results": results}, indent=2, ensure_ascii=False))
    con.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
