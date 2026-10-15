#!/usr/bin/env python3
"""Sync the lab's content to Google Drive (free 15 GB, account aerismusic8@gmail.com).

Drive access needs an OAuth token bound to the account, so the one-time consent
is K's to give (same gate as YouTube, project rule 5 — AX will not use credential
evasion). After that this runs unattended.

Auth, in order of preference:
  1. secrets/drive_token.json     — a Google OAuth "authorized user" token
     (install with: python3 pipeline/drive_sync.py --install-token <path>)
  2. rclone remote named by $AX_DRIVE_REMOTE (default: "axdrive") configured with
     `rclone config` (drive backend).

Usage:
    python3 pipeline/drive_sync.py --status
    python3 pipeline/drive_sync.py --upload            # push content/ to Drive
    python3 pipeline/drive_sync.py --upload --only-art # just the art cache
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import toolchain  # noqa: F401,E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRETS = os.path.join(ROOT, "secrets")
TOKEN = os.path.join(SECRETS, "drive_token.json")
DRIVE_FOLDER = os.environ.get("AX_DRIVE_FOLDER", "AX Content Lab")
REMOTE = os.environ.get("AX_DRIVE_REMOTE", "axdrive")


def _rclone() -> str | None:
    return shutil.which("rclone") or shutil.which("rclone", path=os.path.expanduser("~/.local/bin"))


def status() -> dict:
    rc = _rclone()
    remotes: list[str] = []
    if rc:
        try:
            out = subprocess.run([rc, "listremotes"], capture_output=True, text=True, timeout=30)
            remotes = [r.rstrip(":") for r in out.stdout.splitlines()]
        except Exception:  # noqa: BLE001
            pass
    return {
        "rclone_installed": bool(rc),
        "rclone_path": rc,
        "oauth_token_present": os.path.isfile(TOKEN),
        "rclone_remotes": remotes,
        "drive_remote_ready": REMOTE in remotes,
        "ready": bool(rc) and (os.path.isfile(TOKEN) or REMOTE in remotes),
    }


def _sync_with_rclone(subdir: str, dest_sub: str) -> int:
    rc = _rclone()
    if not rc:
        print("[drive] BLOCKED: rclone not installed", file=sys.stderr)
        return 2
    src = os.path.join(ROOT, subdir)
    dest = f"{REMOTE}:{DRIVE_FOLDER}/{dest_sub}"
    cmd = [rc, "copy", src, dest, "--drive-acknowledge-abuse", "--transfers", "4", "-v"]
    print(f"[drive] {src} -> {dest}")
    return subprocess.run(cmd).returncode


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--upload", action="store_true")
    ap.add_argument("--only-art", action="store_true")
    ap.add_argument("--install-token", metavar="PATH")
    a = ap.parse_args()

    if a.install_token:
        os.makedirs(SECRETS, exist_ok=True)
        shutil.copyfile(a.install_token, TOKEN)
        os.chmod(TOKEN, 0o600)
        print("[drive] token installed -> secrets/drive_token.json")
        return 0

    if a.status or not (a.upload):
        print(json.dumps(status(), indent=2))
        if not status()["ready"]:
            print("\n[drive] BLOCKED: needs one-time Google consent.")
            print("[drive] K: run `rclone config` -> new remote -> name 'axdrive' ->")
            print("[drive]    type 'drive' -> scope 'drive.file' or 'drive' -> sign in as")
            print("[drive]    aerismusic8@gmail.com. Then `drive_sync.py --upload` works.")
        return 0

    if a.only_art:
        return _sync_with_rclone("content/assets/aiart", "assets/aiart")
    rc = _sync_with_rclone("content", "content")
    _sync_with_rclone("docs", "docs")
    _sync_with_rclone("brand", "brand")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
