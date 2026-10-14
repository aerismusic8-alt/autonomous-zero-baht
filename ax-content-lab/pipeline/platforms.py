#!/usr/bin/env python3
"""Platform registry and credential status for multi-platform posting.

Every platform here requires a *user-authorized* token. There is no legitimate
free anonymous upload path on any of them, so this module's job is to be honest
about exactly which credential is missing for each platform, and to read that
status from disk rather than guessing.

Credential files (all under secrets/, mode 600, git-ignored):

  youtube_client_secret.json   Google Cloud OAuth client (Desktop app)
  youtube_token.json           cached user token after first consent
  tiktok_client.json           {"client_key": ..., "client_secret": ...}
  tiktok_token.json            cached user token
  meta_client.json             {"app_id": ..., "app_secret": ...}
  meta_token.json              {"access_token": ..., "page_id": ...,
                                "ig_user_id": ...}
"""
from __future__ import annotations

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRETS = os.path.join(ROOT, "secrets")

# platform -> (credential files it needs, human name, what K must do)
PLATFORMS = {
    "youtube": {
        "name": "YouTube",
        "files": ["youtube_client_secret.json", "youtube_token.json"],
        "needs": ("Google Cloud OAuth client (Desktop app) bound to the channel "
                  "account, then one-time browser consent"),
        "api": "YouTube Data API v3 (videos.insert)",
        "cost": "free (quota 10,000 units/day ≈ 6 uploads/day)",
    },
    "tiktok": {
        "name": "TikTok",
        "files": ["tiktok_client.json", "tiktok_token.json"],
        "needs": ("TikTok developer app with the video.upload scope, then "
                  "one-time browser consent"),
        "api": "TikTok Content Posting API (publish/inbox/video/init)",
        "cost": "free",
    },
    "facebook": {
        "name": "Facebook",
        "files": ["meta_client.json", "meta_token.json"],
        "needs": ("Meta app + a Facebook Page, then a Page access token "
                  "(user must authorize)"),
        "api": "Graph API /{page-id}/video_reels",
        "cost": "free",
    },
    "instagram": {
        "name": "Instagram",
        "files": ["meta_client.json", "meta_token.json"],
        "needs": ("Instagram Business/Creator account linked to the same "
                  "Facebook Page; reuses the Meta token"),
        "api": "Graph API /{ig-user-id}/media + media_publish (Reels)",
        "cost": "free",
    },
}

# Which platforms each series should target. Vertical 9:16 suits all four;
# the split is about audience, not format.
DEFAULT_TARGETS = ["youtube", "tiktok", "facebook", "instagram"]


def path(name: str) -> str:
    return os.path.join(SECRETS, name)


def have(name: str) -> bool:
    p = path(name)
    return os.path.isfile(p) and os.path.getsize(p) > 0


def load(name: str) -> dict | None:
    p = path(name)
    if not have(p):
        return None
    try:
        with open(p) as f:
            return json.load(f)
    except Exception:  # noqa: BLE001
        return None


def status() -> dict:
    """Real credential status per platform, read from disk."""
    out = {}
    for key, cfg in PLATFORMS.items():
        missing = [f for f in cfg["files"] if not have(f)]
        out[key] = {
            "name": cfg["name"],
            "ready": not missing,
            "missing": missing,
            "needs_from_k": cfg["needs"] if missing else None,
            "api": cfg["api"],
            "cost": cfg["cost"],
        }
    return out


def ready_platforms() -> list[str]:
    return [k for k, v in status().items() if v["ready"]]


if __name__ == "__main__":
    print(json.dumps(status(), indent=2, ensure_ascii=False))
