#!/usr/bin/env python3
"""Serve the deliverables gallery + a secure credential intake form.

The intake form lets K paste a GitHub PAT (or upload a YouTube OAuth client JSON)
in a browser, over HTTPS, without ever putting the secret into the chat log.

Routes:
    GET  /                      gallery
    GET  /media/...             videos, thumbnails
    GET  /docs/...              documentation
    GET  /connect               credential intake page
    POST /api/intake/<key>      receives the credential, writes to secrets/

The <key> is a random path segment generated at startup and printed once. It is
not itself a secret; it just keeps the endpoint unguessable. The endpoint is
write-only: nothing stored can be read back through it.
"""
from __future__ import annotations
import toolchain  # noqa: F401  (ensures ffmpeg/ffprobe on PATH)

import http.server
import json
import os
import secrets as pysecrets
import socketserver
import sys
import urllib.parse
import webbrowser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
SECRETS = os.path.join(ROOT, "secrets")
INTAKE_KEY = pysecrets.token_urlsafe(12)

CONNECT_PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AX Content Lab — connect a credential</title>
<style>
body{margin:0;background:#06080f;color:#e8eefc;font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif}
.wrap{max-width:620px;margin:0 auto;padding:40px 20px}
h1{font-size:24px;margin:0 0 6px}
p{color:#8fa0c0}
.card{background:#0e1320;border:1px solid #1e2740;border-radius:14px;padding:22px;margin-top:22px}
label{display:block;font-size:13px;color:#8fa0c0;margin-bottom:6px}
input[type=text],input[type=password],textarea{width:100%;box-sizing:border-box;background:#0b1020;border:1px solid #1e2740;color:#e8eefc;border-radius:9px;padding:11px;font-size:14px;font-family:ui-monospace,monospace}
button{margin-top:14px;background:#12203a;border:1px solid #4fd2ff;color:#e8eefc;border-radius:9px;padding:11px 18px;font-size:14px;cursor:pointer}
button:hover{background:#17294a}
#out{margin-top:14px;font-size:14px;white-space:pre-wrap}
.ok{color:#3ddc97}.bad{color:#ff7a7a}
.note{font-size:13px;color:#8fa0c0;margin-top:10px}
code{background:#141a29;padding:2px 6px;border-radius:5px}
</style></head><body><div class="wrap">
<h1>Connect a credential</h1>
<p>Paste the GitHub token here. It is sent over HTTPS straight into the sandbox and written to
<code>secrets/github_pat.txt</code> (mode 600, git-ignored). It never appears in the chat log.</p>

<div class="card">
  <label for="gh">GitHub fine-grained PAT (starts with <code>github_pat_</code>)</label>
  <input id="gh" type="password" placeholder="github_pat_..." autocomplete="off">
  <button onclick="sendGithub()">Save GitHub token</button>
  <div id="out"></div>
</div>

<div class="card">
  <label for="yt">YouTube OAuth client JSON (paste the whole file contents)</label>
  <textarea id="yt" rows="6" placeholder='{"installed":{"client_id":"...","client_secret":"..."}}'></textarea>
  <button onclick="send('youtube','yt','out2')">Save YouTube client</button>
  <div id="out2"></div>
  <div class="note">Step 1 in docs/SETUP_FOR_K.md. Needed to upload to YouTube.</div>
</div>

<div class="card">
  <label for="tk">TikTok client JSON</label>
  <textarea id="tk" rows="3" placeholder='{"client_key":"...","client_secret":"..."}'></textarea>
  <button onclick="send('tiktok','tk','out3')">Save TikTok client</button>
  <div id="out3"></div>
</div>

<div class="card">
  <label for="mt">Meta (Facebook + Instagram) token JSON</label>
  <textarea id="mt" rows="4" placeholder='{"access_token":"EAAG...","page_id":"...","ig_user_id":"..."}'></textarea>
  <button onclick="send('meta','mt','out4')">Save Meta token</button>
  <div id="out4"></div>
  <div class="note">Covers both Facebook Reels and Instagram Reels.</div>
</div>

<div class="note">After saving, tell AX "เสร็จแล้ว" and it will verify and start posting.</div>

<script>
const KEY = "__KEY__";
async function send(kind, inputId, outId){
  const outEl = document.getElementById(outId);
  const value = document.getElementById(inputId).value;
  outEl.className=""; outEl.textContent="saving...";
  try{
    const r = await fetch("/api/intake/"+KEY,{method:"POST",
      headers:{"Content-Type":"application/json"},body:JSON.stringify({kind,value})});
    const j = await r.json();
    outEl.className = j.ok ? "ok" : "bad";
    outEl.textContent = j.message;
  }catch(e){ outEl.className="bad"; outEl.textContent="error: "+e; }
}
function sendGithub(){ send("github","gh","out"); }
</script>
</div></body></html>
"""


def _write_private(path: str, data: str):
    os.makedirs(SECRETS, exist_ok=True)
    try:
        os.chmod(SECRETS, 0o700)
    except OSError:
        pass
    with open(path, "w") as f:
        f.write(data)
    os.chmod(path, 0o600)


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=SITE, **kw)

    def log_message(self, *a):  # quieter logs
        pass

    def _json(self, code: int, payload: dict):
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/connect", "/connect/"):
            body = CONNECT_PAGE.replace("__KEY__", INTAKE_KEY).encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        if path != f"/api/intake/{INTAKE_KEY}":
            self._json(404, {"ok": False, "message": "not found"})
            return
        try:
            n = int(self.headers.get("Content-Length", "0"))
            data = json.loads(self.rfile.read(n) or b"{}")
        except Exception:  # noqa: BLE001
            self._json(400, {"ok": False, "message": "bad request"})
            return

        kind = data.get("kind")
        value = (data.get("value") or "").strip()
        if not value:
            self._json(400, {"ok": False, "message": "empty value"})
            return

        if kind == "github":
            if not value.startswith(("github_pat_", "ghp_", "gho_")):
                self._json(400, {"ok": False,
                                 "message": "does not look like a GitHub token"})
                return
            _write_private(os.path.join(SECRETS, "github_pat.txt"), value + "\n")
            self._json(200, {"ok": True,
                             "message": "Saved to secrets/github_pat.txt. Tell AX 'done'."})
        elif kind == "youtube":
            try:
                parsed = json.loads(value)
            except Exception:  # noqa: BLE001
                self._json(400, {"ok": False, "message": "not valid JSON"})
                return
            if "installed" not in parsed and "web" not in parsed:
                self._json(400, {"ok": False,
                                 "message": "missing 'installed' or 'web' key"})
                return
            _write_private(os.path.join(SECRETS, "youtube_client_secret.json"), value)
            self._json(200, {"ok": True,
                             "message": "Saved. Tell AX 'done' to start YouTube uploads."})
        elif kind == "tiktok":
            try:
                parsed = json.loads(value)
            except Exception:  # noqa: BLE001
                self._json(400, {"ok": False, "message": "not valid JSON"})
                return
            if not (parsed.get("client_key") and parsed.get("client_secret")):
                self._json(400, {"ok": False,
                                 "message": "needs client_key and client_secret"})
                return
            _write_private(os.path.join(SECRETS, "tiktok_client.json"), value)
            self._json(200, {"ok": True, "message": "Saved TikTok client."})
        elif kind == "meta":
            try:
                parsed = json.loads(value)
            except Exception:  # noqa: BLE001
                self._json(400, {"ok": False, "message": "not valid JSON"})
                return
            if not parsed.get("access_token"):
                self._json(400, {"ok": False, "message": "needs access_token"})
                return
            _write_private(os.path.join(SECRETS, "meta_token.json"), value)
            self._json(200, {"ok": True,
                             "message": "Saved Meta token (Facebook + Instagram)."})
        else:
            self._json(400, {"ok": False, "message": "unknown kind"})


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main() -> int:
    port = int(os.environ.get("PORT", "12000"))
    public = os.environ.get(
        "PUBLIC_URL", "https://work-1-vrswmageirdabiwu.prod-runtime.all-hands.dev")
    os.makedirs(SECRETS, exist_ok=True)
    try:
        os.chmod(SECRETS, 0o700)
    except OSError:
        pass

    with Server(("0.0.0.0", port), Handler) as httpd:
        print(f"[serve] gallery   : {public}/")
        print(f"[serve] intake    : {public}/connect")
        print(f"[serve] intake key: {INTAKE_KEY}")
        sys.stdout.flush()
        httpd.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
