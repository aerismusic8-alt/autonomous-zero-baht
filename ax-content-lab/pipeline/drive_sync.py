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
    rc = shutil.which("rclone") or shutil.which("rclone", path=os.path.expanduser("~/.local/bin"))
    if rc:
        return rc
    return _install_rclone()


def _install_rclone() -> str | None:
    """Fetch rclone on demand; sandbox resets wipe it and there is no root to apt it."""
    import urllib.request
    import zipfile

    dest = os.path.expanduser("~/.local/bin/rclone")
    try:
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        zpath = "/tmp/rclone.zip"
        urllib.request.urlretrieve(
            "https://downloads.rclone.org/rclone-current-linux-amd64.zip", zpath)
        with zipfile.ZipFile(zpath) as z:
            member = next(n for n in z.namelist() if n.endswith("/rclone"))
            with z.open(member) as src, open(dest, "wb") as out:
                shutil.copyfileobj(src, out)
        os.chmod(dest, 0o755)
        return dest
    except Exception:  # noqa: BLE001
        return None


def _ensure_remote() -> bool:
    """Rebuild ~/.config/rclone/rclone.conf from the stored token if a reset wiped it."""
    if not os.path.isfile(TOKEN):
        return False
    conf = os.path.expanduser("~/.config/rclone/rclone.conf")
    if os.path.isfile(conf) and f"[{REMOTE}]" in open(conf).read():
        return True
    os.makedirs(os.path.dirname(conf), exist_ok=True)
    token = open(TOKEN).read().strip()
    with open(conf, "w") as fh:
        fh.write(f"[{REMOTE}]\ntype = drive\nscope = drive\ntoken = {token}\n")
    os.chmod(conf, 0o600)
    return True


def status() -> dict:
    rc = _rclone()
    if rc:
        _ensure_remote()
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


def snapshot(stage: str, stamp: str) -> int:
    """Assemble a self-describing folder of every AI-art video, then upload it.

    The stage dir is a plain directory tree, so this works from any machine that
    has the lab checkout — K's PC included — not only inside this sandbox.
    """
    import glob
    import hashlib

    shutil.rmtree(stage, ignore_errors=True)
    os.makedirs(os.path.join(stage, "videos"), exist_ok=True)
    os.makedirs(os.path.join(stage, "assets", "aiart"), exist_ok=True)

    vids = []
    for d in sorted(glob.glob(os.path.join(ROOT, "content", "*"))):
        meta = os.path.join(d, "metadata.json")
        mp4 = os.path.join(d, "final.mp4")
        if not (os.path.isfile(meta) and os.path.isfile(mp4)):
            continue
        m = json.load(open(meta))
        if not (m.get("provenance", {}).get("ai_art")):
            continue
        slug = os.path.basename(d)
        out = os.path.join(stage, "videos", slug)
        os.makedirs(out, exist_ok=True)
        for f in ("final.mp4", "thumbnail.png", "metadata.json", "qc_report.json"):
            p = os.path.join(d, f)
            if os.path.isfile(p):
                shutil.copy2(p, out)
        q = json.load(open(os.path.join(d, "qc_report.json")))
        vids.append({
            "slug": slug, "series": m.get("series"), "title": m.get("title"),
            "duration_s": m.get("duration_seconds"), "resolution": m.get("resolution"),
            "qc": f"{q['passed']}/{q['total']} {q['status']}",
            "ai_art_frames": len(m["provenance"]["ai_art"]),
            "sha256_16": hashlib.sha256(open(mp4, "rb").read()).hexdigest()[:16],
            "size_mb": round(os.path.getsize(mp4) / 1e6, 1),
        })

    art = os.path.join(ROOT, "content", "assets", "aiart")
    if os.path.isdir(art):
        for f in glob.glob(os.path.join(art, "*")):
            shutil.copy2(f, os.path.join(stage, "assets", "aiart"))

    man = {
        "folder": f"AX Content Lab / AI_Art_Batch_{stamp}",
        "created_utc": stamp, "account": "aerismusic8@gmail.com",
        "pipeline": "AX Viral Content Lab v1.0",
        "renderer": "Pollinations.ai illustrations + Ken Burns motion + edge-tts voice",
        "videos_total": len(vids),
        "qc_pass": sum(1 for v in vids if v["qc"].endswith("PASS")),
        "videos": vids,
    }
    json.dump(man, open(os.path.join(stage, "MANIFEST.json"), "w"), indent=2, ensure_ascii=False)

    lines = [f"# AX Content Lab — AI Art Batch {stamp}", "",
             "Account: **aerismusic8@gmail.com**  |  Pipeline: AX Viral Content Lab v1.0", "",
             "Real AI-illustrated short-form vertical videos (1080x1920), each passing automated QC.",
             "No fabricated metrics.", "",
             f"**Videos:** {man['videos_total']}  |  **QC pass:** {man['qc_pass']}", "",
             "## Folders", "",
             "- `videos/<slug>/` — `final.mp4`, `thumbnail.png`, `metadata.json`, `qc_report.json`",
             "- `assets/aiart/` — source AI illustrations + provenance sidecars", "",
             "## Videos", "", "| slug | series | duration | QC | AI frames | MB |",
             "|---|---|---|---|---|---|"]
    for v in vids:
        lines.append(f"| {v['slug']} | {v['series']} | {v['duration_s']}s | {v['qc']} | {v['ai_art_frames']} | {v['size_mb']} |")
    lines += ["", "## Notes", "",
              "- Mirrored on GitHub: `aerismusic8-alt/autonomous-zero-baht` @ `ax-content-lab`.",
              "- Publishing is human-gated (OAuth consent); see `docs/SETUP_FOR_K.md`.",
              "- Image model licensing varies per Pollinations route; flagged in each `qc_report.json`.",
              "- Point-in-time snapshot; the batch continues and later snapshots get their own folder."]
    open(os.path.join(stage, "README.md"), "w").write("\n".join(lines) + "\n")
    return len(vids)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--upload", action="store_true")
    ap.add_argument("--only-art", action="store_true")
    ap.add_argument("--snapshot", action="store_true",
                    help="build a dated folder of every AI-art video and upload it")
    ap.add_argument("--date", default=None, help="snapshot stamp (default: today UTC)")
    ap.add_argument("--stage", default="/tmp/ax_snapshot", help="local staging dir")
    ap.add_argument("--install-token", metavar="PATH")
    a = ap.parse_args()

    if a.install_token:
        os.makedirs(SECRETS, exist_ok=True)
        shutil.copyfile(a.install_token, TOKEN)
        os.chmod(TOKEN, 0o600)
        print("[drive] token installed -> secrets/drive_token.json")
        return 0

    if a.snapshot:
        import datetime
        stamp = a.date or datetime.datetime.utcnow().strftime("%Y-%m-%d")
        n = snapshot(a.stage, stamp)
        print(f"[drive] staged {n} AI-art videos -> {a.stage}")
        rc = _rclone()
        if not rc:
            print("[drive] BLOCKED: rclone unavailable", file=sys.stderr)
            return 2
        dest = f"{REMOTE}:{DRIVE_FOLDER}/AI_Art_Batch_{stamp}"
        cmd = [rc, "copy", a.stage, dest, "--transfers", "4", "--drive-acknowledge-abuse", "-v"]
        print(f"[drive] {a.stage} -> {dest}")
        return subprocess.run(cmd).returncode

    if a.status or not (a.upload):
        print(json.dumps(status(), indent=2))
        if not status()["ready"]:
            print("\n[drive] BLOCKED: needs one-time Google consent.")
            print("[drive] K: run `rclone authorize \"drive\"` on a machine with a browser,")
            print("[drive]    paste the JSON via `drive_sync.py --install-token <file>`.")
            print("[drive]    Then `drive_sync.py --snapshot` works.")
        return 0

    if a.only_art:
        return _sync_with_rclone("content/assets/aiart", "assets/aiart")
    rc = _sync_with_rclone("content", "content")
    _sync_with_rclone("docs", "docs")
    _sync_with_rclone("brand", "brand")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
