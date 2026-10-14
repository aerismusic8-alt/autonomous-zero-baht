#!/usr/bin/env python3
"""Credential bridge + channel setup verifier.

This is the *only* place AX needs K. K supplies tokens once; everything after
that is automatic. Secrets are stored only in git-ignored `secrets/` and never
printed.

Usage:
    python3 pipeline/connect.py status                  # show what is connected
    python3 pipeline/connect.py github --token <PAT>    # store a repo-write PAT
    python3 pipeline/connect.py youtube --client <path> # install OAuth client JSON
    python3 pipeline/connect.py check                   # verify each connection live
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRETS = os.path.join(ROOT, "secrets")
GH_PAT = os.path.join(SECRETS, "github_pat.txt")
YT_CLIENT = os.path.join(SECRETS, "youtube_client_secret.json")
YT_TOKEN = os.path.join(SECRETS, "youtube_token.json")
PLATFORM_TOKENS = os.path.join(SECRETS, "platform_tokens.json")


def _ensure_secrets_dir():
    os.makedirs(SECRETS, exist_ok=True)
    try:
        os.chmod(SECRETS, stat.S_IRWXU)
    except OSError:
        pass


def _write_private(path: str, data: str):
    _ensure_secrets_dir()
    with open(path, "w") as f:
        f.write(data)
    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)


def status() -> dict:
    st = {
        "github_pat": os.path.isfile(GH_PAT),
        "youtube_oauth_client": os.path.isfile(YT_CLIENT),
        "youtube_token": os.path.isfile(YT_TOKEN),
        "other_platform_tokens": os.path.isfile(PLATFORM_TOKENS),
    }
    st["ready_to_publish_youtube"] = st["youtube_oauth_client"] or st["youtube_token"]
    return st


def check() -> dict:
    """Live-verify each connection. Never prints the secret itself."""
    out = {}

    # GitHub
    tok = None
    if os.path.isfile(GH_PAT):
        tok = open(GH_PAT).read().strip()
    tok = tok or os.environ.get("GITHUB_TOKEN")
    if tok:
        r = subprocess.run(
            ["curl", "-s", "-m", "15", "-i", "-H", f"Authorization: Bearer {tok}",
             "https://api.github.com/user"], capture_output=True, text=True)
        body = r.stdout
        # split headers from body on the last blank line
        if "\r\n\r\n" in body:
            body = body.rsplit("\r\n\r\n", 1)[-1]
        elif "\n\n" in body:
            body = body.rsplit("\n\n", 1)[-1]
        scopes = ""
        for line in r.stdout.splitlines():
            if line.lower().startswith("x-oauth-scopes:"):
                scopes = line.split(":", 1)[1].strip()
        login = ""
        try:
            login = json.loads(body).get("login", "")
        except Exception:  # noqa: BLE001
            pass

        # Capability probe: fine-grained PATs do NOT report x-oauth-scopes, so the
        # only reliable test is an actual write attempt. Create + delete a throwaway
        # branch ref on the target repo.
        repo = os.environ.get("AX_REPO", "aerismusic8-alt/autonomous-zero-baht")
        base = subprocess.run(
            ["curl", "-s", "-m", "15", "-H", f"Authorization: Bearer {tok}",
             f"https://api.github.com/repos/{repo}"], capture_output=True, text=True)
        default_sha = ""
        try:
            default_sha = json.loads(base.stdout).get("default_branch", "main")
        except Exception:  # noqa: BLE001
            default_sha = "main"
        sha = subprocess.run(
            ["curl", "-s", "-m", "15", "-H", f"Authorization: Bearer {tok}",
             f"https://api.github.com/repos/{repo}/commits/{default_sha}"],
            capture_output=True, text=True)
        try:
            sha_val = json.loads(sha.stdout)["sha"]
        except Exception:  # noqa: BLE001
            sha_val = ""
        can_push = False
        probe_detail = "could not resolve base commit"
        if sha_val:
            probe_ref = "refs/heads/ax-write-probe"
            cr = subprocess.run(
                ["curl", "-s", "-m", "15", "-o", "/dev/null", "-w", "%{http_code}",
                 "-X", "POST", "-H", f"Authorization: Bearer {tok}",
                 "-H", "Accept: application/vnd.github+json",
                 f"https://api.github.com/repos/{repo}/git/refs",
                 "-d", json.dumps({"ref": probe_ref, "sha": sha_val})],
                capture_output=True, text=True)
            code = cr.stdout.strip()
            if code in ("201", "422"):  # 422 = ref already exists, still means write works
                can_push = True
                probe_detail = "write probe succeeded (created probe branch)"
                subprocess.run(
                    ["curl", "-s", "-m", "15", "-o", "/dev/null", "-X", "DELETE",
                     "-H", f"Authorization: Bearer {tok}",
                     f"https://api.github.com/repos/{repo}/git/refs/heads/ax-write-probe"],
                    capture_output=True, text=True)
            else:
                probe_detail = f"write probe returned HTTP {code}"

        out["github"] = {
            "authenticated": bool(login),
            "login": login,
            "scopes_header": scopes or "(not reported - normal for fine-grained PATs)",
            "can_push": can_push,
            "probe": probe_detail,
            "source": "secrets/github_pat.txt" if os.path.isfile(GH_PAT) else "environment GITHUB_TOKEN",
        }
    else:
        out["github"] = {"authenticated": False}

    # YouTube
    if os.path.isfile(YT_TOKEN):
        out["youtube"] = {"token_present": True,
                          "note": "run: python3 pipeline/publisher.py --all --privacy private"}
    elif os.path.isfile(YT_CLIENT):
        out["youtube"] = {"client_present": True,
                          "note": "next publish run will open a one-time consent URL"}
    else:
        out["youtube"] = {"client_present": False,
                          "action_needed": "K: create Google Cloud OAuth client -> secrets/youtube_client_secret.json"}

    if os.path.isfile(PLATFORM_TOKENS):
        try:
            keys = list(json.load(open(PLATFORM_TOKENS)).keys())
        except Exception:  # noqa: BLE001
            keys = []
        out["other_platforms"] = {"configured": keys}
    return out


def install_youtube_client(src: str):
    if not os.path.isfile(src):
        raise SystemExit(f"file not found: {src}")
    _ensure_secrets_dir()
    shutil.copyfile(src, YT_CLIENT)
    os.chmod(YT_CLIENT, stat.S_IRUSR | stat.S_IWUSR)
    return YT_CLIENT


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["status", "check", "github", "youtube"])
    ap.add_argument("--token")
    ap.add_argument("--client")
    args = ap.parse_args()

    if args.action == "status":
        print(json.dumps(status(), indent=2))
    elif args.action == "check":
        print(json.dumps(check(), indent=2, ensure_ascii=False))
    elif args.action == "github":
        if not args.token:
            raise SystemExit("--token required")
        _write_private(GH_PAT, args.token.strip() + "\n")
        print(json.dumps({"stored": "secrets/github_pat.txt",
                          "next": "run: python3 pipeline/connect.py check"}, indent=2))
    elif args.action == "youtube":
        if not args.client:
            raise SystemExit("--client <path to downloaded OAuth JSON> required")
        print(json.dumps({"installed": install_youtube_client(args.client)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
