#!/usr/bin/env python3
"""Build a public gallery site for the AX Viral Content Lab deliverables.

Creates `site/` containing:
    index.html              - gallery with inline players, status, docs
    media/<slug>/final.mp4  - the produced videos
    media/<slug>/thumb.png  - thumbnails
    docs/*.md               - documentation
    code.zip                - the full pipeline source

NEVER copies secrets/. Only original work produced by this project.
"""
from __future__ import annotations

import glob
import html
import json
import os
import shutil
import sys
import zipfile
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

CSS = """
:root{--bg:#06080f;--card:#0e1320;--line:#1e2740;--txt:#e8eefc;--dim:#8fa0c0;--acc:#4fd2ff;--ok:#3ddc97;--warn:#ffb84d}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--txt);font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:var(--acc);text-decoration:none}a:hover{text-decoration:underline}
.wrap{max-width:1180px;margin:0 auto;padding:28px 20px 80px}
header{border-bottom:1px solid var(--line);padding-bottom:22px;margin-bottom:28px}
h1{margin:0 0 6px;font-size:30px;letter-spacing:-.4px}
.sub{color:var(--dim);font-size:14px}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:22px 0 8px}
.stat{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px}
.stat .n{font-size:26px;font-weight:700}
.stat .l{color:var(--dim);font-size:12px;text-transform:uppercase;letter-spacing:.6px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:18px;margin-top:26px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;overflow:hidden;display:flex;flex-direction:column}
.card video{width:100%;aspect-ratio:9/16;background:#000;display:block;object-fit:cover}
.card .body{padding:12px 14px 14px}
.card h3{margin:0 0 4px;font-size:15px}
.card .meta{color:var(--dim);font-size:12px;margin-bottom:8px}
.badge{display:inline-block;font-size:11px;padding:2px 8px;border-radius:99px;border:1px solid var(--line)}
.badge.ok{color:var(--ok);border-color:#1c4d3a;background:#0d2a1e}
.badge.warn{color:var(--warn);border-color:#4d3a1c;background:#2a210d}
section{margin-top:44px}
h2{font-size:20px;border-left:3px solid var(--acc);padding-left:12px;margin-bottom:14px}
.box{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 18px}
ul{margin:8px 0;padding-left:22px}li{margin:5px 0}
code{background:#141a29;padding:2px 6px;border-radius:5px;font-size:13px}
pre{background:#0b1020;border:1px solid var(--line);border-radius:10px;padding:14px;overflow:auto;font-size:13px}
.links{display:flex;flex-wrap:wrap;gap:10px;margin-top:12px}
.btn{display:inline-block;background:#12203a;border:1px solid var(--line);border-radius:9px;padding:9px 14px;font-size:13px;color:var(--txt)}
.btn:hover{border-color:var(--acc);text-decoration:none}
footer{margin-top:60px;color:var(--dim);font-size:12px;border-top:1px solid var(--line);padding-top:18px}
"""


def build() -> dict:
    if os.path.exists(SITE):
        shutil.rmtree(SITE)
    os.makedirs(os.path.join(SITE, "media"), exist_ok=True)
    os.makedirs(os.path.join(SITE, "docs"), exist_ok=True)

    items = []
    for d in sorted(glob.glob(os.path.join(ROOT, "content", "*"))):
        mp = os.path.join(d, "metadata.json")
        vp = os.path.join(d, "final.mp4")
        tp = os.path.join(d, "thumbnail.png")
        qp = os.path.join(d, "qc_report.json")
        if not (os.path.isfile(mp) and os.path.isfile(vp)):
            continue
        meta = json.load(open(mp))
        qc = json.load(open(qp)) if os.path.isfile(qp) else {}
        slug = meta["slug"]
        md = os.path.join(SITE, "media", slug)
        os.makedirs(md, exist_ok=True)
        shutil.copyfile(vp, os.path.join(md, "final.mp4"))
        if os.path.isfile(tp):
            shutil.copyfile(tp, os.path.join(md, "thumb.png"))
        items.append({
            "slug": slug,
            "title": meta.get("title", slug),
            "series": meta.get("series", ""),
            "duration": meta.get("duration_seconds"),
            "resolution": meta.get("resolution"),
            "size_mb": round(os.path.getsize(vp) / 1e6, 1),
            "qc": f"{qc.get('passed','?')}/{qc.get('total','?')}",
            "qc_status": qc.get("status", "NONE"),
            "description": meta.get("description", ""),
            "tags": meta.get("tags", []),
        })

    # docs
    for p in glob.glob(os.path.join(ROOT, "docs", "*.md")):
        shutil.copyfile(p, os.path.join(SITE, "docs", os.path.basename(p)))
    if os.path.isfile(os.path.join(ROOT, "README.md")):
        shutil.copyfile(os.path.join(ROOT, "README.md"), os.path.join(SITE, "docs", "README.md"))

    # code zip (no secrets, no media)
    zpath = os.path.join(SITE, "code.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for folder in ("pipeline", "content/specs", "docs", ".github", "brand", "research"):
            base = os.path.join(ROOT, folder)
            for dp, _, fns in os.walk(base):
                if "secrets" in dp or "__pycache__" in dp:
                    continue
                for fn in fns:
                    fp = os.path.join(dp, fn)
                    z.write(fp, os.path.relpath(fp, ROOT))
        for f in ("README.md", "AGENTS.md", "run_loop.sh", ".gitignore"):
            fp = os.path.join(ROOT, f)
            if os.path.isfile(fp):
                z.write(fp, f)

    produced = len(items)
    passed = sum(1 for i in items if i["qc_status"] == "PASS")
    built = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    cards = []
    for i in items:
        badge = (f'<span class="badge ok">QC {i["qc"]} PASS</span>'
                 if i["qc_status"] == "PASS" else
                 f'<span class="badge warn">QC {i["qc"]} {i["qc_status"]}</span>')
        cards.append(f"""
      <article class="card">
        <video controls preload="metadata" playsinline poster="media/{i['slug']}/thumb.png">
          <source src="media/{i['slug']}/final.mp4" type="video/mp4">
        </video>
        <div class="body">
          <h3>{html.escape(i['title'])}</h3>
          <div class="meta">{html.escape(i['series'])} &middot; {i['duration']}s &middot; {i['resolution']} &middot; {i['size_mb']} MB</div>
          {badge}
          <div class="links">
            <a class="btn" href="media/{i['slug']}/final.mp4" download>Download MP4</a>
            <a class="btn" href="media/{i['slug']}/thumb.png" target="_blank">Thumbnail</a>
          </div>
        </div>
      </article>""")

    page = f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AX Viral Content Lab — Deliverables</title>
<style>{CSS}</style>
</head><body><div class="wrap">
<header>
  <h1>AX Viral Content Lab</h1>
  <div class="sub">Autonomous, zero-cost content studio &middot; built {built}</div>
  <div class="stats">
    <div class="stat"><div class="n">{produced}</div><div class="l">Videos produced</div></div>
    <div class="stat"><div class="n">{passed}/{produced}</div><div class="l">Passed QC</div></div>
    <div class="stat"><div class="n">0</div><div class="l">Published</div></div>
    <div class="stat"><div class="n">&#3647;0.00</div><div class="l">Verified revenue</div></div>
  </div>
  <div class="sub">Every number above is evidence-backed. QC runs on the rendered file itself
  (frame brightness/variance, silence detection, loudness). Nothing is claimed without proof.</div>
</header>

<section>
  <h2>Produced work</h2>
  <div class="grid">{''.join(cards)}
  </div>
</section>

<section>
  <h2>Status and what is blocked</h2>
  <div class="box">
    <p><strong>Published: 0.</strong> Publishing is blocked because every platform requires an
    OAuth token bound to the account holder's identity. No platform offers a legitimate anonymous
    upload path, and this project will not use credential-evasion tools.</p>
    <p>AX has already written and tested the YouTube uploader end to end
    (<code>pipeline/publisher.py</code>). It stops exactly at the auth boundary.</p>
    <p><strong>Revenue: &#3647;0.00.</strong> No monetisation channel is active. Prerequisites
    (1,000 subscribers + 4,000 watch-hours or 10M Shorts views) cannot be assessed before
    publishing starts.</p>
  </div>
</section>

<section>
  <h2>What K needs to do (~10 minutes, all free)</h2>
  <div class="box">
    <ol>
      <li><strong>GitHub write token</strong> &mdash; create a fine-grained PAT
      (Contents + Workflows: Read and write), then run
      <code>python3 pipeline/connect.py github --token github_pat_XXXX</code></li>
      <li><strong>YouTube OAuth client</strong> &mdash; create it in Google Cloud Console, then run
      <code>python3 pipeline/connect.py youtube --client &lt;path&gt;</code></li>
      <li><strong>Create the channel</strong> &mdash; branding assets are ready in <code>brand/</code></li>
    </ol>
    <p>Full steps: <a href="docs/SETUP_FOR_K.md">docs/SETUP_FOR_K.md</a></p>
  </div>
</section>

<section>
  <h2>Documentation and source</h2>
  <div class="box">
    <div class="links">
      <a class="btn" href="code.zip" download>Download source (code.zip)</a>
      <a class="btn" href="docs/STATUS.md">STATUS</a>
      <a class="btn" href="docs/MARKET_RESEARCH.md">Market research</a>
      <a class="btn" href="docs/TOOLS.md">Tools inventory</a>
      <a class="btn" href="docs/PUBLISHING.md">Publishing</a>
      <a class="btn" href="docs/SETUP_FOR_K.md">Setup for K</a>
      <a class="btn" href="docs/README.md">README</a>
    </div>
    <p style="margin-top:14px">All narrative text is original writing. All music is synthesised
    from scratch with NumPy. All visuals are drawn procedurally with PIL. No third-party footage,
    music, script or image is used. Public platform metadata is used for research only.</p>
  </div>
</section>

<footer>AX Viral Content Lab &middot; generated {built} &middot; code MIT</footer>
</div></body></html>
"""
    with open(os.path.join(SITE, "index.html"), "w") as f:
        f.write(page)

    return {"site": SITE, "videos": produced, "qc_pass": passed,
            "code_zip_mb": round(os.path.getsize(zpath) / 1e6, 2)}


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
