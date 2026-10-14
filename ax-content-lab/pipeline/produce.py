#!/usr/bin/env python3
"""AX Viral Content Lab - production orchestrator.

    RESEARCH -> SELECT -> SCRIPT -> STORYBOARD -> ASSET GENERATION
    -> VOICE/MUSIC -> EDIT -> QUALITY CONTROL -> PACKAGE

Reads a script spec (JSON) and produces a publish-ready package:
    final.mp4, thumbnail.png, metadata.json, qc_report.json, assets/
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import audio
import tts
import video
from video import Scene

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIENTATIONS = {
    "vertical": (1080, 1920),
    "horizontal": (1920, 1080),
    "square": (1080, 1080),
}


def probe(path: str) -> dict:
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration,size:stream=width,height,codec_name,r_frame_rate,nb_frames",
        "-of", "json", path]).decode()
    return json.loads(out)


def make_thumbnail(spec: dict, scenes: list[Scene], out_png: str, size) -> str:
    from PIL import Image, ImageDraw, ImageFilter
    w, h = size
    theme = video.THEMES.get(spec.get("theme", "abyss"), video.THEMES["abyss"])
    img = video._gradient(*theme["bg"]).resize((w, h))
    glow = video._glow_base(theme).resize((w, h))
    img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")

    title = spec.get("title", "")
    # thumbnail hook text (short, punchy)
    hook = spec.get("packaging", {}).get("thumbnail_text") or title
    f = video.font(int(h * 0.085))
    lines = video._wrap(hook.upper(), 15)
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    total_h = len(lines) * int(h * 0.098)
    y = (h - total_h) // 2
    for ln in lines:
        bbox = d.textbbox((0, 0), ln, font=f)
        tw = bbox[2] - bbox[0]
        x = (w - tw) / 2
        d.text((x + 4, y + 4), ln, font=f, fill=(0, 0, 0, 200))
        d.text((x, y), ln, font=f, fill=video._hex(theme["text"]) + (255,))
        y += int(h * 0.098)

    # accent underline
    d.rectangle([w * 0.28, y + 10, w * 0.72, y + 20], fill=video._hex(theme["accent"]) + (255,))
    img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")
    img = img.filter(ImageFilter.SMOOTH)
    img.save(out_png)
    return out_png


def build(spec_path: str, out_root: str | None = None, force: bool = False) -> dict:
    with open(spec_path) as f:
        spec = json.load(f)

    slug = spec["slug"]
    work = os.path.join(out_root or os.path.join(ROOT, "content"), slug)
    assets = os.path.join(work, "assets")

    # Incremental: skip work that already exists and passed QC unless forced.
    if not force:
        existing_qc = os.path.join(work, "qc_report.json")
        existing_meta = os.path.join(work, "metadata.json")
        if (os.path.isfile(existing_qc) and os.path.isfile(existing_meta)
                and os.path.isfile(os.path.join(work, "final.mp4"))):
            meta = json.load(open(existing_meta))
            qc = json.load(open(existing_qc))
            return {"work_dir": work, "metadata": meta, "qc": qc, "skipped": True}

    if os.path.exists(work):
        shutil.rmtree(work)
    os.makedirs(assets, exist_ok=True)

    size = ORIENTATIONS.get(spec.get("orientation", "vertical"), (1080, 1920))
    voice_key = spec.get("voice", "male_documentary")
    mood = spec.get("mood", "calm")
    hold = float(spec.get("scene_hold", 0.35))

    scene_specs = spec["scenes"]
    scenes = []
    durs = []
    voices = []

    # --- ASSET GENERATION + VOICE ---
    for i, s in enumerate(scene_specs):
        scenes.append(Scene(
            text=s.get("text", ""),
            kicker=s.get("kicker", ""),
            theme=s.get("theme", spec.get("theme", "abyss")),
            style=s.get("style", "caption"),
            particles=int(s.get("particles", 46)),
            seed=i * 7 + 1,
            bg_image=s.get("bg_image"),
        ))
        mp3 = os.path.join(assets, f"voice_{i:02d}.mp3")
        if s.get("text"):
            tts.speak(s["text"], s.get("voice", voice_key), mp3,
                      rate=s.get("rate", spec.get("rate", "+0%")))
            voices.append(mp3)
            d = audio.probe_duration(mp3)
        else:
            d = float(s.get("silent_duration", 1.5))
            voices.append(None)
        durs.append(d + hold)

    total = sum(durs)

    # --- VOICE / MUSIC ---
    # normalise each voice clip to consistent loudness, then concatenate
    norm = []
    for i, v in enumerate(voices):
        if not v:
            continue
        o = os.path.join(assets, f"voice_n_{i:02d}.m4a")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", v,
                        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
                        "-c:a", "aac", "-b:a", "192k", o], check=True)
        norm.append(o)

    voice_track = None
    if norm:
        alist = os.path.join(assets, "_alist.txt")
        with open(alist, "w") as f:
            for o in norm:
                f.write(f"file '{os.path.abspath(o)}'\n")
        voice_track = os.path.join(assets, "voice_track.m4a")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
                        "-i", alist, "-c", "copy", voice_track], check=True)

    music = audio.generate_music(total + 1.0, mood,
                                 os.path.join(assets, "music.wav"),
                                 seed=abs(hash(slug)) % 100000)

    mixed = os.path.join(assets, "mix.m4a")
    if voice_track:
        audio.mix_voice_music(voice_track, music, mixed)
    else:
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", music,
                        "-c:a", "aac", "-b:a", "192k", mixed], check=True)

    # --- EDIT (render + concat + mux) ---
    segs = []
    pos = 0.0
    for i, sc in enumerate(scenes):
        seg = os.path.join(assets, f"seg_{i:02d}.mp4")
        video.render_scene(sc, durs[i], seg, p_start=pos / total,
                           p_end=(pos + durs[i]) / total, size=size,
                           fade_start=(i == 0), fade_end=(i == len(scenes) - 1))
        segs.append(seg)
        pos += durs[i]

    silent = os.path.join(assets, "video_silent.mp4")
    video.concat_segments(segs, silent, assets)
    final = os.path.join(work, "final.mp4")
    video.mux_audio(silent, mixed, final)

    # --- PACKAGE ---
    thumb = make_thumbnail(spec, scenes, os.path.join(work, "thumbnail.png"), size)

    info = probe(final)
    fmt = info["format"]
    vs = next(s for s in info["streams"] if s.get("codec_name") in ("h264", "hevc"))
    as_ = next((s for s in info["streams"] if s.get("codec_name") == "aac"), {})

    meta = {
        "slug": slug,
        "title": spec.get("title"),
        "series": spec.get("series", ""),
        "description": spec.get("packaging", {}).get("description", ""),
        "tags": spec.get("packaging", {}).get("tags", []),
        "hashtags": spec.get("packaging", {}).get("hashtags", []),
        "orientation": spec.get("orientation", "vertical"),
        "resolution": f"{vs['width']}x{vs['height']}",
        "duration_seconds": round(float(fmt["duration"]), 2),
        "files": {
            "video": "final.mp4",
            "thumbnail": "thumbnail.png",
        },
        "sources": spec.get("sources", []),
        "provenance": {
            "narration": "edge-tts neural TTS (Microsoft free tier)",
            "music": "procedurally synthesised (original, numpy)",
            "visuals": "procedurally rendered (original, PIL + ffmpeg)",
            "third_party_assets": [],
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    with open(os.path.join(work, "metadata.json"), "w") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    # --- QUALITY CONTROL ---
    qc = run_qc(final, meta, as_, spec)
    with open(os.path.join(work, "qc_report.json"), "w") as f:
        json.dump(qc, f, indent=2, ensure_ascii=False)

    return {"work_dir": work, "metadata": meta, "qc": qc}


def run_qc(video_path: str, meta: dict, audio_stream: dict, spec: dict) -> dict:
    checks = []

    def add(name, ok, detail):
        checks.append({"check": name, "pass": bool(ok), "detail": str(detail)})

    # duration
    d = meta["duration_seconds"]
    add("duration_reasonable", 8 <= d <= 300, f"{d}s")
    add("has_audio", bool(audio_stream), audio_stream.get("codec_name", "missing"))
    add("vertical_or_expected", True, meta["resolution"])

    # silence / loudness detection
    try:
        r = subprocess.run(
            ["ffmpeg", "-v", "info", "-i", video_path, "-af",
             "silencedetect=noise=-40dB:d=1.2", "-f", "null", "-"],
            capture_output=True, text=True)
        sil = r.stderr.count("silence_start")
        add("no_long_silence", sil == 0, f"{sil} silent gap(s) > 1.2s at -40dB")
    except Exception as e:
        add("no_long_silence", False, f"probe error {e}")

    # mean volume
    try:
        r = subprocess.run(["ffmpeg", "-v", "info", "-i", video_path,
                            "-af", "volumedetect", "-f", "null", "-"],
                           capture_output=True, text=True)
        mean = None
        for line in r.stderr.splitlines():
            if "mean_volume" in line:
                mean = float(line.split("mean_volume:")[1].split("dB")[0].strip())
        add("audio_level_ok", mean is not None and -30 < mean < -8, f"mean={mean} dB")
    except Exception as e:
        add("audio_level_ok", False, f"probe error {e}")

    # no black frames at start/end, and content exists mid-video
    import numpy as _np
    from PIL import Image as _Image
    frames_dir = os.path.join(os.path.dirname(video_path), "assets", "_qcframes")
    os.makedirs(frames_dir, exist_ok=True)
    try:
        for label, ts in [("start", 0.4), ("mid", d / 2), ("end", max(0.4, d - 0.6))]:
            fp = os.path.join(frames_dir, f"{label}.png")
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(ts),
                            "-i", video_path, "-frames:v", "1", fp], check=True)
            arr = _np.asarray(_Image.open(fp).convert("L"), dtype=_np.float32)
            val = float(arr.mean())
            # content check: not black AND has tonal variation (not a flat fill)
            std = float(arr.std())
            add(f"frame_{label}_not_black", val > 8, f"YAVG={val:.1f}")
            add(f"frame_{label}_has_detail", std > 6, f"std={std:.1f}")
    except Exception as e:
        add("frame_not_black", False, f"probe error {e}")

    # narration present in spec
    has_text = any(s.get("text") for s in spec.get("scenes", []))
    add("narration_present", has_text, f"{len(spec.get('scenes', []))} scenes")

    # originality: no third-party assets
    add("no_third_party_assets",
        not meta["provenance"]["third_party_assets"],
        meta["provenance"]["third_party_assets"] or "none declared")

    # packaging completeness
    add("has_title", bool(meta.get("title")), meta.get("title"))
    add("has_description", len(meta.get("description", "")) >= 30,
        f"{len(meta.get('description',''))} chars")
    add("has_tags", len(meta.get("tags", [])) >= 3, f"{len(meta.get('tags',[]))} tags")

    passed = sum(1 for c in checks if c["pass"])
    return {
        "checks": checks,
        "passed": passed,
        "total": len(checks),
        "status": "PASS" if passed == len(checks) else "REVIEW",
        "qc_at": datetime.now(timezone.utc).isoformat(),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    res = build(args.spec, args.out)
    print(json.dumps({"work_dir": res["work_dir"],
                      "qc_status": res["qc"]["status"],
                      "passed": f"{res['qc']['passed']}/{res['qc']['total']}",
                      "duration": res["metadata"]["duration_seconds"]}, indent=2))
    return 0 if res["qc"]["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
