#!/usr/bin/env python3
"""Build site/references.html from the latest research/references_*.json.

Renders clickable cards with the real public metrics we pulled, so K can review
the reference videos in a browser.
"""
from __future__ import annotations

import glob
import html
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")

# Niche display order and a one-line note on what to copy (the pattern, not the work).
NOTES = {
    "Shorts - horror/scary": "Cold open on the threat, no intro. First line is a question or a warning.",
    "Shorts - space": "One scale comparison per beat. Numbers as the punchline.",
    "Shorts - history": "Correct a belief the viewer already holds. 'You were taught wrong.'",
    "Shorts - what-if": "State the premise in the first 2 seconds, then escalate one consequence per beat.",
    "Shorts - mystery": "Present the evidence, withhold the answer, end on the open question.",
    "Scary stories (animated)": "Animated true-story format: narrator + simple motion art, 2-4 min.",
    "Space facts": "Rapid fact stack. Each fact 15-20 s. Visual changes every fact.",
    "History facts": "Myth-correction list format. High retention because viewers argue in comments.",
    "What-if / physics": "Hypothetical premise, step-by-step consequence chain.",
    "Unsolved mysteries": "Case file structure: what we know, what doesn't fit, what remains open.",
    "AI animated story": "AI-assisted art with a human-written emotional arc. Story > visuals.",
}

# Niches that are vertical short-form.
SHORT_PREFIX = "Shorts - "


def fmt(n) -> str:
    if n is None:
        return "—"
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


def engagement(v) -> str:
    if not v.get("views") or not v.get("likes"):
        return "—"
    return f"{v['likes'] / v['views'] * 100:.1f}%"


def card(v: dict) -> str:
    title = html.escape((v.get("title") or "")[:95])
    ch = html.escape((v.get("channel") or "")[:40])
    url = html.escape(v.get("url") or "#")
    dur = f"{v['duration_s']}s" if v.get("duration_s") else "—"
    date = v.get("upload_date") or ""
    if len(date) == 8:
        date = f"{date[:4]}-{date[4:6]}-{date[6:]}"
    return f"""    <a class="rcard" href="{url}" target="_blank" rel="noopener">
      <div class="rtitle">{title}</div>
      <div class="rch">{ch}</div>
      <div class="rmetrics">
        <span><b>{fmt(v.get('views'))}</b> views</span>
        <span><b>{fmt(v.get('likes'))}</b> likes</span>
        <span><b>{fmt(v.get('comments'))}</b> comments</span>
        <span><b>{engagement(v)}</b> like/view</span>
        <span>{dur}</span><span>{date}</span>
      </div>
    </a>"""


def section(niche: str, items: list[dict]) -> str:
    note = NOTES.get(niche, "")
    kind = "Vertical short-form" if niche.startswith(SHORT_PREFIX) else "Long-form"
    head = f"<h2>{html.escape(niche.replace(SHORT_PREFIX, ''))}</h2>"
    sub = (f'<p class="note"><span class="tag">{kind}</span> {html.escape(note)}</p>'
           if note else f'<p class="note"><span class="tag">{kind}</span></p>')
    cards = "\n".join(card(v) for v in items[:8])
    return f'<section>{head}{sub}<div class="rgrid">\n{cards}\n</div></section>'


def main() -> int:
    files = sorted(glob.glob(os.path.join(ROOT, "research", "references_*.json")))
    if not files:
        print("no references_*.json found; run pipeline/references.py first")
        return 1
    with open(files[-1]) as f:
        data = json.load(f)

    niches = data["niches"]
    total = sum(len(v) for v in niches.values())

    # Shorts first, then long-form.
    order = ([k for k in niches if k.startswith(SHORT_PREFIX)]
             + [k for k in niches if not k.startswith(SHORT_PREFIX)])

    body = "\n".join(section(k, niches[k]) for k in order)
    stamp = data.get("collected_at", "")[:19].replace("T", " ")

    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AX Content Lab — reference videos</title>
<style>
:root{{--bg:#06080f;--card:#0e1320;--line:#1e2740;--fg:#e8eefc;--dim:#8fa0c0;--acc:#4fd2ff}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--fg);
font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif}}
.wrap{{max-width:1180px;margin:0 auto;padding:34px 20px 70px}}
a{{color:var(--acc)}}
h1{{font-size:27px;margin:0 0 8px}}
h2{{font-size:19px;margin:34px 0 4px;border-left:3px solid var(--acc);padding-left:11px}}
p{{color:var(--dim)}}
.note{{margin:2px 0 14px;font-size:13.5px}}
.tag{{display:inline-block;background:#12203a;border:1px solid #24406b;color:var(--acc);
border-radius:20px;padding:1px 10px;font-size:11.5px;margin-right:8px}}
.rgrid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:12px}}
.rcard{{display:block;background:var(--card);border:1px solid var(--line);border-radius:12px;
padding:14px;text-decoration:none;color:inherit;transition:border-color .15s,transform .15s}}
.rcard:hover{{border-color:var(--acc);transform:translateY(-2px)}}
.rtitle{{font-weight:600;font-size:14.5px;line-height:1.4;margin-bottom:3px}}
.rch{{color:var(--dim);font-size:12.5px;margin-bottom:9px}}
.rmetrics{{display:flex;flex-wrap:wrap;gap:5px 12px;font-size:12px;color:var(--dim)}}
.rmetrics b{{color:var(--fg)}}
.hero{{background:linear-gradient(135deg,#0e1a2e,#0e1320);border:1px solid var(--line);
border-radius:14px;padding:20px;margin-bottom:8px}}
.back{{display:inline-block;margin-bottom:18px;font-size:13px}}
.warn{{background:#1a1408;border:1px solid #4a3a12;border-radius:10px;padding:12px 14px;
font-size:13px;color:#e8d9a8;margin-top:16px}}
</style></head><body><div class="wrap">
<a class="back" href="./">&larr; back to the gallery</a>
<div class="hero">
  <h1>Reference videos — real high-performing examples</h1>
  <p>{total} videos across {len(niches)} niches. Public YouTube metadata pulled live with
  yt-dlp on {stamp} UTC. Click any card to open the video.</p>
  <p>These are <b>references to study</b> — the structure, pacing and hook. No footage, music
  or script from them is downloaded or reused. Everything we publish is original.</p>
  <div class="warn"><b>Views are a reach signal, not proof of revenue.</b> We never treat view
  counts as earnings, and we never copy a video's content — only learn the pattern.</div>
</div>
{body}
<footer style="margin-top:50px;color:var(--dim);font-size:12.5px">
AX Viral Content Lab &middot; raw evidence: research/{os.path.basename(files[-1])}</footer>
</div></body></html>
"""
    os.makedirs(SITE, exist_ok=True)
    out = os.path.join(SITE, "references.html")
    with open(out, "w") as f:
        f.write(page)
    print(json.dumps({"page": out, "niches": len(niches), "total": total}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
