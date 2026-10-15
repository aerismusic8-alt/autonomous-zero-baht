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
TT_CLIENT = os.path.join(SECRETS, "tiktok_client.json")
TT_TOKEN = os.path.join(SECRETS, "tiktok_token.json")
TT_REDIRECT = os.environ.get("AX_TT_REDIRECT", "https://localhost/")
TT_AUTH = "https://www.tiktok.com/v2/auth/authorize/"
TT_TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
TT_SCOPES = "video.upload,user.info.basic"


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


def _google_tokeninfo(access_token: str) -> dict:
    r = subprocess.run(
        ["curl", "-s", "-m", "20",
         f"https://oauth2.googleapis.com/tokeninfo?access_token={access_token}"],
        capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except Exception:  # noqa: BLE001
        return {"error": "unparseable tokeninfo response"}


def install_youtube_token(src: str, client_id: str = "", client_secret: str = ""):
    """Convert a token from OAuth Playground (or any JSON with access/refresh
    tokens) into the authorized-user file google-auth expects, after verifying
    it actually carries the youtube.upload scope."""
    raw = open(src).read() if os.path.isfile(src) else src
    data = json.loads(raw)
    at = data.get("access_token") or data.get("token")
    if not at:
        raise SystemExit("token JSON has no access_token")

    info = _google_tokeninfo(at)
    scopes = info.get("scope", "").split()
    if "https://www.googleapis.com/auth/youtube.upload" not in scopes:
        raise SystemExit(
            f"token lacks youtube.upload scope; has: {scopes or info}")
    if not data.get("refresh_token"):
        raise SystemExit("token has no refresh_token; it will expire in ~1h. "
                         "Re-copy the JSON that includes refresh_token.")

    out = {
        "token": at,
        "refresh_token": data["refresh_token"],
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": data.get("client_id") or client_id,
        "client_secret": data.get("client_secret") or client_secret,
        "scopes": ["https://www.googleapis.com/auth/youtube.upload"],
    }
    if not (out["client_id"] and out["client_secret"]):
        raise SystemExit("token JSON has no client_id/client_secret; the refresh "
                         "will fail. Include them, or pass --client-id/--client-secret.")
    _write_private(YT_TOKEN, json.dumps(out, indent=2))
    return {"stored": "secrets/youtube_token.json", "scopes": scopes,
            "verified": True}


def install_tiktok_client(src: str):
    """Store the TikTok app credentials and print the authorization URL."""
    if os.path.isfile(src):
        data = json.loads(open(src).read())
    else:
        data = json.loads(src)
    key = data.get("client_key") or data.get("client_id")
    secret = data.get("client_secret")
    if not (key and secret):
        raise SystemExit("need client_key and client_secret")
    _write_private(TT_CLIENT, json.dumps({"client_key": key, "client_secret": secret},
                                         indent=2))
    return {"stored": "secrets/tiktok_client.json",
            "authorize_url": tiktok_auth_url()}


def tiktok_auth_url() -> str:
    import urllib.parse

    cli = json.loads(open(TT_CLIENT).read())
    params = {
        "client_key": cli["client_key"],
        "scope": TT_SCOPES,
        "response_type": "code",
        "redirect_uri": TT_REDIRECT,
        "state": "axlab",
    }
    return TT_AUTH + "?" + urllib.parse.urlencode(params)


def install_tiktok_token(code: str):
    """Exchange a pasted authorization code for tokens and store them."""
    import urllib.parse
    import urllib.request

    cli = json.loads(open(TT_CLIENT).read())
    body = urllib.parse.urlencode({
        "client_key": cli["client_key"],
        "client_secret": cli["client_secret"],
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": TT_REDIRECT,
    }).encode()
    req = urllib.request.Request(TT_TOKEN_URL, data=body, headers={
        "Content-Type": "application/x-www-form-urlencoded"})
    try:
        resp = json.loads(urllib.request.urlopen(req, timeout=30).read())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"token exchange failed: {e.code} {e.read()[:300]}")
    if resp.get("error") or not resp.get("access_token"):
        raise SystemExit(f"token exchange returned no access_token: {resp}")
    _write_private(TT_TOKEN, json.dumps({
        "access_token": resp["access_token"],
        "refresh_token": resp.get("refresh_token", ""),
        "open_id": resp.get("open_id", ""),
        "expires_in": resp.get("expires_in"),
        "scope": resp.get("scope", TT_SCOPES),
    }, indent=2))
    return {"stored": "secrets/tiktok_token.json", "open_id": resp.get("open_id"),
            "scope": resp.get("scope"), "verified": True}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["status", "check", "github", "youtube",
                                       "youtube-token", "tiktok", "tiktok-url",
                                       "tiktok-code"])
    ap.add_argument("--token")
    ap.add_argument("--client")
    ap.add_argument("--client-id", default="")
    ap.add_argument("--client-secret", default="")
    ap.add_argument("--code", default="")
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
    elif args.action == "youtube-token":
        if not (args.token or args.client):
            raise SystemExit("--token <path or JSON string> required")
        print(json.dumps(install_youtube_token(args.token or args.client,
                                               args.client_id, args.client_secret),
                         indent=2))
    elif args.action == "tiktok":
        if not args.client:
            raise SystemExit("--client <path or JSON string with client_key+client_secret>")
        print(json.dumps(install_tiktok_client(args.client), indent=2))
    elif args.action == "tiktok-url":
        if not os.path.isfile(TT_CLIENT):
            raise SystemExit("no secrets/tiktok_client.json yet; run 'tiktok' first")
        print(tiktok_auth_url())
    elif args.action == "tiktok-code":
        if not args.code:
            raise SystemExit("--code <authorization code> required")
        print(json.dumps(install_tiktok_token(args.code), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
