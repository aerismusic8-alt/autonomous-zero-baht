#!/usr/bin/env python3
"""AI art generation for AX Viral Content Lab.

Turns a scene description into a real illustrated image (anime / 3D / painterly)
using Pollinations.ai - an open-source, no-signup, no-key image endpoint. This is
the layer that was missing: previous renders were a gradient plus captions, with
no actual imagery.

Every generated file gets a sidecar JSON with the exact prompt, seed, model and a
sha256, so a frame can be reproduced and its provenance audited. Files are cached
by content hash, so re-runs never re-fetch.

Licensing note (recorded per asset in the sidecar):
  - Pollinations platform code is MIT and the public endpoint is free/no-key.
  - The hosted endpoint returns whatever free model it routes to; individual
    model licences vary. We therefore treat outputs as "provider-returned art
    for review" and keep the prompt+seed so any asset can be regenerated or
    dropped. Do not ship to a paid channel until K confirms the model licence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "content", "assets", "aiart")
ENDPOINT = "https://image.pollinations.ai/prompt"
PROVIDER = "pollinations.ai"

# Style anchors that keep a series visually consistent across scenes.
STYLES = {
    "anime": (
        "anime style, 1990s cel animation, hand-drawn, clean line art, "
        "muted cinematic palette, dramatic lighting"
    ),
    "anime-horror": (
        "anime style horror illustration, 1990s dark cel animation, high contrast, "
        "eerie rim light, desaturated palette, unsettling atmosphere"
    ),
    "3d": (
        "3d render, cinematic octane render, volumetric light, subsurface scattering, "
        "detailed materials, film still"
    ),
    "3d-anime": (
        "3d anime render, cel-shaded cgi, stylised proportions, cinematic lighting, "
        "detailed background"
    ),
    "storybook": (
        "storybook illustration, gouache painting, textured brushwork, warm palette, "
        "cinematic composition"
    ),
    "retro-sci": (
        "retro sci-fi illustration, 1970s airbrush poster art, nebula, film grain, "
        "dramatic scale"
    ),
}


def _slug_hash(*parts: str) -> str:
    return hashlib.sha256("|".join(parts).encode()).hexdigest()[:16]


def _url(prompt: str, seed: int, w: int, h: int, model: str) -> str:
    q = urllib.parse.urlencode({
        "width": w, "height": h, "seed": seed, "model": model,
        "nologo": "true", "nofeed": "true", "enhance": "false",
    })
    return f"{ENDPOINT}/{urllib.parse.quote(prompt)}?{q}"


def generate(prompt: str, style: str = "anime", seed: int = 0,
             width: int = 1080, height: int = 1920, model: str = "flux",
             tries: int = 14, wait: float = 6.0, out_dir: str | None = None,
             verbose: bool = True) -> dict:
    """Generate one image. Returns a record dict with the local path."""
    anchor = STYLES.get(style, STYLES["anime"])
    full = f"{prompt}, {anchor}, no text, no watermark"
    key = _slug_hash(full, str(seed), str(width), str(height), model)
    out_dir = out_dir or CACHE
    os.makedirs(out_dir, exist_ok=True)
    img_path = os.path.join(out_dir, f"{key}.jpg")
    meta_path = os.path.join(out_dir, f"{key}.json")

    if os.path.exists(img_path) and os.path.getsize(img_path) > 5000:
        rec = json.load(open(meta_path)) if os.path.exists(meta_path) else {}
        rec["cached"] = True
        if verbose:
            print(f"[aiart] cache hit {key}")
        return rec

    url = _url(full, seed, width, height, model)
    last = ""
    for attempt in range(1, tries + 1):
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
                data = r.read()
                if r.status == 200 and len(data) > 5000:
                    with open(img_path, "wb") as f:
                        f.write(data)
                    rec = {
                        "key": key, "path": img_path, "prompt": full,
                        "base_prompt": prompt, "style": style, "seed": seed,
                        "model": model, "width": width, "height": height,
                        "provider": PROVIDER, "url": url,
                        "sha256": hashlib.sha256(data).hexdigest(),
                        "bytes": len(data), "attempts": attempt,
                        "generated_at": datetime.now(timezone.utc).isoformat(),
                        "license_note": ("pollinations.ai public endpoint; platform MIT; "
                                         "model licence varies - review before monetised use"),
                        "cached": False,
                    }
                    json.dump(rec, open(meta_path, "w"), indent=1)
                    if verbose:
                        print(f"[aiart] {key} ok attempt={attempt} {len(data)}b")
                    return rec
                last = f"status {r.status}"
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}"
        except Exception as e:  # noqa: BLE001
            last = str(e)
        time.sleep(wait)
    raise RuntimeError(f"aiart failed after {tries} tries for {key}: {last}")


def generate_series(shots: list[dict], out_dir: str | None = None,
                    model: str = "flux", wait: float = 6.0) -> list[dict]:
    """Generate a list of shots, each {prompt, style?, seed?}. Sequential with
    pacing so a burst does not trip the fair-use limiter."""
    recs = []
    for i, s in enumerate(shots):
        rec = generate(s["prompt"], style=s.get("style", "anime"),
                       seed=s.get("seed", i + 1), out_dir=out_dir,
                       model=model, wait=wait)
        recs.append(rec)
        time.sleep(1.5)
    return recs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=False)
    ap.add_argument("--style", default="anime", choices=sorted(STYLES))
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--width", type=int, default=1080)
    ap.add_argument("--height", type=int, default=1920)
    ap.add_argument("--model", default="flux")
    ap.add_argument("--shots", help="JSON file: [{prompt, style, seed}]")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    if a.shots:
        shots = json.load(open(a.shots))
        recs = generate_series(shots, out_dir=a.out, model=a.model)
        print(json.dumps(recs, indent=1))
        return 0
    if not a.prompt:
        ap.error("--prompt or --shots required")
    rec = generate(a.prompt, a.style, a.seed, a.width, a.height, a.model,
                   out_dir=a.out)
    print(json.dumps(rec, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
