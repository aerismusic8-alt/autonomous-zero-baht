#!/usr/bin/env python3
"""Scene renderer: builds vertical short-form videos from scene scripts.

Each scene is drawn frame-by-frame with PIL (animated gradient glow, drifting
particles, animated captions, vignette, progress bar) and piped straight into
ffmpeg as raw RGB. No stock footage, no third-party assets -> fully original.
"""
from __future__ import annotations
import toolchain  # noqa: F401  (ensures ffmpeg/ffprobe on PATH)

import math
import os
import subprocess
import textwrap
from dataclasses import dataclass, field

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
FPS = 30
BG_ZOOM_PAD = 0.16  # extra frame on each axis so Ken Burns can pan without edges
BG_ZOOM_MIN = 0.0   # Ken Burns zoom at the first frame
BG_ZOOM_MAX = 0.06  # Ken Burns zoom at the last frame (slow push-in)

FONT_DIRS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]

THEMES = {
    "abyss":    {"bg": ("#020a14", "#07203a"), "glow": "#2ea8ff", "text": "#eaf6ff", "accent": "#4fd2ff"},
    "void":     {"bg": ("#0a0414", "#22093a"), "glow": "#a15cff", "text": "#f4ecff", "accent": "#c48cff"},
    "ember":    {"bg": ("#150404", "#3a0d0a"), "glow": "#ff5a2e", "text": "#fff0e8", "accent": "#ff9a6b"},
    "forest":   {"bg": ("#03120c", "#0a2e1c"), "glow": "#2fd08a", "text": "#eafff4", "accent": "#5ff0ac"},
    "sepia":    {"bg": ("#14100a", "#3a2c14"), "glow": "#e0b45a", "text": "#fff6e0", "accent": "#ffd98a"},
    "signal":   {"bg": ("#050510", "#101030"), "glow": "#5f7bff", "text": "#eef1ff", "accent": "#8aa0ff"},
    "aurora":   {"bg": ("#020d12", "#062a33"), "glow": "#25e0d0", "text": "#e8fffb", "accent": "#5ff0e0"},
}


def _hex(c: str) -> tuple[int, int, int]:
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    for p in FONT_DIRS:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                continue
    return ImageFont.load_default()


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _gradient(top, bottom) -> Image.Image:
    col = np.zeros((H, 1, 3), dtype=np.float32)
    for y in range(H):
        t = y / (H - 1)
        col[y, 0] = _lerp(_hex(top), _hex(bottom), t)
    img = np.repeat(col, W, axis=1).astype(np.uint8)
    return Image.fromarray(img, "RGB")


def _shift(layer: Image.Image, dx: int, dy: int) -> Image.Image:
    """Translate an RGBA layer, wrapping at the edges."""
    return layer.transform(
        layer.size, Image.AFFINE, (1, 0, -dx, 0, 1, -dy),
        resample=Image.BILINEAR)


def _vignette() -> Image.Image:
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    cx, cy = W / 2, H / 2
    d = np.sqrt(((xx - cx) / (W * 0.62)) ** 2 + ((yy - cy) / (H * 0.62)) ** 2)
    v = np.clip(1.15 - 0.75 * d ** 2, 0.18, 1.0)
    return Image.fromarray((v * 255).astype(np.uint8), "L")


@dataclass
class Scene:
    text: str = ""
    kicker: str = ""
    theme: str = "abyss"
    style: str = "caption"      # caption | title | quote | endcard
    particles: int = 46
    bg_image: str | None = None
    seed: int = 0
    hold: float = 0.0


def _wrap(text: str, width: int) -> list[str]:
    out = []
    for para in text.split("\n"):
        out.extend(textwrap.wrap(para, width=width) or [""])
    return out


def _text_layer(lines, f, color, cx, top, line_h, align="center", max_w=None):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    y = top
    for ln in lines:
        bbox = d.textbbox((0, 0), ln, font=f)
        w = bbox[2] - bbox[0]
        x = cx - w / 2 if align == "center" else cx
        d.text((x, y), ln, font=f, fill=color)
        y += line_h
    return layer


def _particles(n, seed, accent):
    rng = np.random.default_rng(seed)
    ps = []
    for _ in range(n):
        ps.append({
            "x": float(rng.uniform(0, W)),
            "y": float(rng.uniform(0, H)),
            "r": float(rng.uniform(1.5, 5.5)),
            "vy": float(rng.uniform(18, 70)),
            "drift": float(rng.uniform(-14, 14)),
            "alpha": float(rng.uniform(0.18, 0.7)),
        })
    return ps


def _glow_base(theme) -> Image.Image:
    """Soft radial glow baked once, then translated per frame."""
    g = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(g)
    cx, cy = W // 2, int(H * 0.42)
    for i in range(26, 0, -1):
        r = i * 46
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=int(255 * (1 - i / 27) * 0.5))
    g = g.filter(ImageFilter.GaussianBlur(90))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer.paste(Image.new("RGBA", (W, H), _hex(theme["glow"]) + (255,)), (0, 0), g)
    return layer


def render_scene(scene: Scene, dur: float, out_mp4: str, fps: int = FPS,
                 p_start: float = 0.0, p_end: float = 1.0, show_progress: bool = True,
                 size=(W, H), fade_start: bool = False, fade_end: bool = False) -> str:
    w, h = size
    theme = THEMES.get(scene.theme, THEMES["abyss"])
    n_frames = max(2, int(dur * fps))

    if scene.bg_image and os.path.exists(scene.bg_image):
        src = Image.open(scene.bg_image).convert("RGB")
        # upscale first so Ken Burns cropping always has pixels to move into
        base = src.resize((int(w * (1 + BG_ZOOM_PAD)), int(h * (1 + BG_ZOOM_PAD))),
                          Image.LANCZOS)
        has_art = True
    else:
        base = _gradient(*theme["bg"])
        has_art = False

    vig = _vignette().resize((w, h))
    glow = _glow_base(theme).resize((w, h))
    parts = _particles(scene.particles, scene.seed, theme["accent"])

    # text geometry
    if scene.style == "title":
        f = font(int(h * 0.072))
        lines = _wrap(scene.text, 18)
        lh = int(h * 0.088)
        top = int(h * 0.36)
    elif scene.style == "quote":
        f = font(int(h * 0.050), bold=False)
        lines = _wrap(scene.text, 26)
        lh = int(h * 0.066)
        top = int(h * 0.40)
    elif scene.style == "endcard":
        f = font(int(h * 0.050))
        lines = _wrap(scene.text, 24)
        lh = int(h * 0.066)
        top = int(h * 0.42)
    else:  # caption
        f = font(int(h * 0.049))
        lines = _wrap(scene.text, 22)
        lh = int(h * 0.064)
        top = int(h * 0.66)

    txt = _text_layer(lines, f, _hex(theme["text"]) + (255,), w / 2, top, lh)
    if scene.style == "title":
        txt = txt.filter(ImageFilter.GaussianBlur(0))

    kf = font(int(h * 0.026))
    kicker_layer = None
    if scene.kicker:
        kicker_layer = _text_layer([scene.kicker.upper()], kf,
                                   _hex(theme["accent"]) + (235,), w / 2, int(h * 0.16),
                                   int(h * 0.036))
        # letter spacing
        kicker_layer = kicker_layer

    accent_rgb = _hex(theme["accent"])
    bar_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))

    proc = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(fps), "-i", "-",
        "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p", out_mp4,
    ], stdin=subprocess.PIPE)

    fade_in = min(0.45, dur * 0.35) if fade_start else 0.0
    fade_out = min(0.35, dur * 0.3) if fade_end else 0.0
    for i in range(n_frames):
        t = i / fps
        # --- background: slow Ken Burns move across the AI art, else drifting glow ---
        if has_art:
            p = i / max(1, n_frames - 1)
            easeP = p * p * (3 - 2 * p)
            zoom = 1.0 + BG_ZOOM_MIN + (BG_ZOOM_MAX - BG_ZOOM_MIN) * easeP
            cw, ch = int(w * zoom), int(h * zoom)
            ox = int((base.width - cw) * (0.15 + 0.7 * p))
            oy = int((base.height - ch) * (0.5 + 0.35 * math.sin(scene.seed + p * 3)))
            ox = max(0, min(base.width - cw, ox))
            oy = max(0, min(base.height - ch, oy))
            frame = base.crop((ox, oy, ox + cw, oy + ch)).resize((w, h), Image.BILINEAR)
            # gentle glow only, so the art stays visible
            gx = int(math.sin(t * 0.4 + scene.seed) * w * 0.04)
            gy = int(math.cos(t * 0.3 + scene.seed) * h * 0.03)
            frame = Image.alpha_composite(frame.convert("RGBA"), _shift(glow, gx, gy)).convert("RGB")
        else:
            gx = int(math.sin(t * 0.5 + scene.seed) * w * 0.10)
            gy = int(math.cos(t * 0.38 + scene.seed) * h * 0.05)
            frame = base.copy()
            frame.paste(glow, (gx, gy), glow)

        # --- particles ---
        ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        for p in parts:
            py = (p["y"] - p["vy"] * t) % h
            px = (p["x"] + p["drift"] * math.sin(t * 0.6 + p["x"]) * 0.5) % w
            r = p["r"]
            a = int(255 * p["alpha"] * (0.55 + 0.45 * math.sin(t * 1.6 + p["x"])))
            a = max(0, min(255, a))
            d.ellipse([px - r, py - r, px + r, py + r], fill=accent_rgb + (a,))
        frame = Image.alpha_composite(frame.convert("RGBA"), ov)

        # --- text ---
        tl = txt.copy()
        appear = 1.0 if fade_in <= 0 else min(1.0, t / fade_in)
        ease = appear * appear * (3 - 2 * appear)
        slide = int((1 - ease) * h * 0.02)
        tl = tl.transform((w, h), Image.AFFINE, (1, 0, 0, 0, 1, -slide),
                          resample=Image.BILINEAR)
        alpha = int(255 * ease)
        if alpha > 0:
            a_ch = tl.getchannel("A").point(lambda v: v * alpha // 255)
            tl.putalpha(a_ch)
            frame = Image.alpha_composite(frame, tl)
        if kicker_layer is not None:
            frame = Image.alpha_composite(frame, kicker_layer)

        # --- progress bar ---
        if show_progress:
            bar_layer.paste((0, 0, 0, 0), (0, 0, w, h))
            db = ImageDraw.Draw(bar_layer)
            prog = p_start + (p_end - p_start) * (i / max(1, n_frames - 1))
            by = h - int(h * 0.012)
            db.rectangle([0, by, w, by + int(h * 0.006)], fill=(255, 255, 255, 45))
            db.rectangle([0, by, int(w * prog), by + int(h * 0.006)], fill=accent_rgb + (230,))
            frame = Image.alpha_composite(frame, bar_layer)

        # --- vignette + global fade ---
        rgb = frame.convert("RGB")
        rgb = Image.composite(rgb, Image.new("RGB", (w, h), (0, 0, 0)), vig)
        fade = 1.0
        if t < fade_in:
            fade = min(fade, t / max(1e-6, fade_in))
        if t > dur - fade_out:
            fade = min(fade, (dur - t) / max(1e-6, fade_out))
        if fade < 1.0:
            rgb = Image.blend(Image.new("RGB", (w, h), (0, 0, 0)), rgb, max(0.0, fade))

        proc.stdin.write(rgb.tobytes())

    proc.stdin.close()
    proc.wait()
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg scene encode failed: {out_mp4}")
    return out_mp4


def concat_segments(segments: list[str], out_path: str, workdir: str) -> str:
    lst = os.path.join(workdir, "_concat.txt")
    with open(lst, "w") as f:
        for s in segments:
            f.write(f"file '{os.path.abspath(s)}'\n")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
                    "-i", lst, "-c", "copy", out_path], check=True)
    return out_path


def mux_audio(video: str, audio: str, out_path: str) -> str:
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", video, "-i", audio,
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
                    out_path], check=True)
    return out_path
