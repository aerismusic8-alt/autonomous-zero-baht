#!/usr/bin/env python3
"""Visual prompt pools per series.

Each pool is a set of original, on-theme scene descriptions. A spec gets one
prompt per scene, chosen by position so the imagery progresses with the story
(establishing shot -> closer -> reveal -> final). Prompts describe *visuals*
only; they never reuse any third-party plot, character or artwork.

`attach(spec)` fills scene["art_prompt"] / scene["art_style"] in place and
returns the spec, so every spec renders with illustrated art.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# style anchor used by aiart.STYLES
SERIES_STYLE = {
    "Deep Space Logs": "retro-sci",
    "Quiet Horror Files": "anime-horror",
    "Cosmic Wonders": "3d",
    "Unsolved Archive": "storybook",
    "What If Physics": "3d",
}

# Ordered visual beats: [establish, tense, detail, reveal, memory, final]
POOLS = {
    "Deep Space Logs": [
        "a lone deep-space probe drifting in black void, faint distant Earth, cinematic wide shot",
        "a cold dim mission control room at night, one glowing monitor, empty chairs, blue screen light",
        "an empty holographic star map with unmapped coordinates over darkness, ominous",
        "a radio telescope dish under a vast starry night sky, faint signal glow, eerie",
        "an ageing launch facility at dawn, rocket on the pad, nostalgic haze, wide establishing shot",
        "a silent probe silhouette against a vast nebula, stars, quiet and final",
    ],
    "Quiet Horror Files": [
        "a lonely lighthouse on a black cliff at night, beam sweeping the sea, heavy fog, ominous",
        "an open handwritten logbook on a wooden desk, single oil lamp, long shadows",
        "an empty coastal village at dusk, no people, curtains moving, unsettling calm",
        "a staircase descending into darkness, faint light below, damp stone walls",
        "a reflection in a dark window that does not match the room, horror",
        "a lighthouse gone dark at the edge of a storm, waves heavy, final dread",
    ],
    "Cosmic Wonders": [
        "a colossal nebula in deep space, towering pillars of gas, stars, awe-inspiring wide shot",
        "a planet's rings seen from close orbit, sharp sunlight, detailed surface below",
        "a black hole warping starlight, accretion disk, gravitational lensing, cinematic",
        "countless galaxies scattered across the void, tiny foreground spacecraft for scale",
        "a supernova blooming among the stars, brilliant expanding light",
        "Earth small and blue against an enormous dark cosmos, quiet final wide shot",
    ],
    "Unsolved Archive": [
        "a rain-soaked city street at night in the 1970s, wet asphalt, lone streetlight",
        "a cluttered detective's desk, photographs and folders under a green desk lamp",
        "an old archive room lined with dusty files, narrow aisle, single bulb",
        "a fog-covered mountain trail where a path abruptly ends, cold light",
        "a faded family photograph on a mantelpiece, one face scratched out",
        "an empty car parked on a remote road at dusk, doors closed, unexplained",
    ],
    "What If Physics": [
        "a sun like an enormous glowing sphere beside a tiny Earth for scale, dramatic",
        "a person standing inside a transparent physics diagram of spacetime, glowing grid",
        "Earth splitting into bands of light as a hypothetical force passes through it",
        "a clock melting into orbiting rings of numbers, surreal physics illustration",
        "light rays bending around a massive object, cosmic lensing diagram in space",
        "a calm Earth from orbit with a subtle glowing field around it, resolved conclusion",
    ],
}


def prompts_for(series: str, n_scenes: int) -> list[str]:
    pool = POOLS.get(series, POOLS["Deep Space Logs"])
    if n_scenes <= len(pool):
        # even sampling so a 6-beat pool fits any scene count
        step = len(pool) / n_scenes
        return [pool[min(len(pool) - 1, int(i * step))] for i in range(n_scenes)]
    return [pool[i % len(pool)] for i in range(n_scenes)]


def attach(spec: dict) -> dict:
    import hashlib
    series = spec.get("series", "Deep Space Logs")
    style = SERIES_STYLE.get(series, "anime")
    scenes = spec.get("scenes", [])
    ps = prompts_for(series, len(scenes))
    # Seed per (slug, scene) so two stories in the same series do not share the
    # same pool image with the same seed (which would yield identical art).
    base = int(hashlib.sha256(spec.get("slug", "").encode()).hexdigest()[:6], 16)
    for i, sc in enumerate(scenes):
        sc.setdefault("art_prompt", ps[i])
        sc.setdefault("art_style", style)
        sc.setdefault("art_seed", (base + i * 7919) % 2_000_000 + 1)
    spec.setdefault("art_style", style)
    return spec


def main() -> int:
    import glob
    changed = 0
    for path in sorted(glob.glob(os.path.join(ROOT, "content", "specs", "*.json"))):
        spec = json.load(open(path))
        # recompute style + seed every run; keep any custom art_prompt intact
        spec.pop("art_style", None)
        for sc in spec.get("scenes", []):
            sc.pop("art_style", None)
            sc.pop("art_seed", None)
        attach(spec)
        json.dump(spec, open(path, "w"), indent=2, ensure_ascii=False)
        changed += 1
    print(json.dumps({"specs_updated": changed}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
