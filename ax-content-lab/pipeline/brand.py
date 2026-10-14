#!/usr/bin/env python3
"""Generate channel brand assets (avatar, banner, end screen) procedurally.

Saves K the design work when creating the channel: the files are ready to upload.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import Image, ImageDraw, ImageFilter  # noqa: E402
import video  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "brand")


def _bg(w, h, theme_key):
    t = video.THEMES[theme_key]
    img = video._gradient(*t["bg"]).resize((w, h))
    glow = video._glow_base(t).resize((w, h))
    return Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB"), t


def avatar(size=800, theme_key="signal"):
    img, t = _bg(size, size, theme_key)
    d = ImageDraw.Draw(img)
    cx = cy = size // 2
    # concentric rings
    for i, r in enumerate([int(size * 0.42), int(size * 0.33), int(size * 0.24)]):
        d.ellipse([cx - r, cy - r, cx + r, cy + r],
                  outline=video._hex(t["accent"]), width=max(2, size // 160))
    # monogram
    f = video.font(int(size * 0.30))
    txt = "AX"
    bbox = d.textbbox((0, 0), txt, font=f)
    d.text((cx - (bbox[2] - bbox[0]) / 2, cy - (bbox[3] - bbox[1]) / 2 - size * 0.02),
           txt, font=f, fill=video._hex(t["text"]))
    # a signal dot
    r = int(size * 0.035)
    d.ellipse([cx - r, cy + int(size * 0.22) - r, cx + r, cy + int(size * 0.22) + r],
              fill=video._hex(t["accent"]))
    p = os.path.join(OUT, "avatar.png")
    img.save(p)
    return p


def banner(w=2560, h=1440, theme_key="signal"):
    """YouTube banner safe area is the central 1546x423 strip."""
    img, t = _bg(w, h, theme_key)
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx = w // 2
    cy = h // 2
    f1 = video.font(int(h * 0.085))
    f2 = video.font(int(h * 0.036), bold=False)
    title = "AX VIRAL CONTENT LAB"
    bbox = d.textbbox((0, 0), title, font=f1)
    d.text((cx - (bbox[2] - bbox[0]) / 2, cy - h * 0.09), title, font=f1,
           fill=video._hex(t["text"]))
    sub = "Original short stories  •  New entries regularly"
    bbox2 = d.textbbox((0, 0), sub, font=f2)
    d.text((cx - (bbox2[2] - bbox2[0]) / 2, cy + h * 0.02), sub, font=f2,
           fill=video._hex(t["accent"]))
    d.rectangle([cx - w * 0.13, cy + h * 0.075, cx + w * 0.13, cy + h * 0.082],
                fill=video._hex(t["accent"]))
    img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")
    p = os.path.join(OUT, "banner.png")
    img.save(p)
    return p


def endcard(w=1080, h=1920, theme_key="signal"):
    img, t = _bg(w, h, theme_key)
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f1 = video.font(int(h * 0.062))
    f2 = video.font(int(h * 0.036), bold=False)
    lines = ["FOLLOW FOR", "THE NEXT", "ENTRY"]
    y = h * 0.34
    for ln in lines:
        bbox = d.textbbox((0, 0), ln, font=f1)
        d.text(((w - (bbox[2] - bbox[0])) / 2, y), ln, font=f1,
               fill=video._hex(t["text"]))
        y += h * 0.078
    sub = "Original stories, written and produced in-house."
    bbox2 = d.textbbox((0, 0), sub, font=f2)
    d.text(((w - (bbox2[2] - bbox2[0])) / 2, y + h * 0.05), sub, font=f2,
           fill=video._hex(t["accent"]))
    img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")
    img = img.filter(ImageFilter.SMOOTH)
    p = os.path.join(OUT, "endcard.png")
    img.save(p)
    return p


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    print(avatar())
    print(banner())
    print(endcard())
