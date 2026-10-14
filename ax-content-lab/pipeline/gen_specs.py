#!/usr/bin/env python3
"""Generate original content specs for the AX Viral Content Lab series.

All narrative text below is original writing produced for this project. Market
research (research/*.json) informs *structure* only (hook length, scene count,
pacing, twist placement) - no third-party plot, script, or media is reused.
"""
from __future__ import annotations

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC_DIR = os.path.join(ROOT, "content", "specs")

SERIES = {
    "Deep Space Logs": {
        "theme": "signal", "mood": "tense", "voice": "male_documentary",
        "tags": ["sci fi short story", "creepy stories", "space horror", "micro fiction",
                 "deep space logs", "science fiction shorts", "twist ending", "short story"],
        "hashtags": ["#scifi", "#shortstory", "#space", "#creepy", "#fiction"],
    },
    "Quiet Horror Files": {
        "theme": "ember", "mood": "dark", "voice": "male_calm",
        "tags": ["horror short story", "creepy stories", "scary story", "micro horror",
                 "twist ending", "short horror", "creepypasta", "bedtime horror"],
        "hashtags": ["#horror", "#creepy", "#shortstory", "#scary", "#twist"],
    },
    "Cosmic Wonders": {
        "theme": "aurora", "mood": "wonder", "voice": "female_calm",
        "tags": ["space facts", "science facts", "astronomy", "universe facts",
                 "space documentary", "mind blowing facts", "science shorts", "cosmos"],
        "hashtags": ["#space", "#science", "#facts", "#universe", "#astronomy"],
    },
    "Unsolved Archive": {
        "theme": "sepia", "mood": "mystery", "voice": "female_news",
        "tags": ["unsolved mystery", "true story", "mystery shorts", "detective",
                 "cold case", "unexplained", "mystery story", "investigation"],
        "hashtags": ["#mystery", "#unsolved", "#truestory", "#detective", "#archive"],
    },
    "What If Physics": {
        "theme": "forest", "mood": "wonder", "voice": "male_warm",
        "tags": ["what if", "physics explained", "science shorts", "hypothetical",
                 "thought experiment", "science facts", "educational shorts", "physics"],
        "hashtags": ["#whatif", "#physics", "#science", "#facts", "#explained"],
    },
}

# (slug, series, title, thumbnail_text, [(kicker, text, style), ...])
PIECES = [
    ("0002_the_lighthouse_log", "Quiet Horror Files", "The Lighthouse Log", "DAY 41",
     [("QUIET HORROR FILES", "The lighthouse keeper wrote in his log every night.", "caption"),
      ("", "Day 41: the light is working. The ships are safe.", "caption"),
      ("", "Day 42: the light is working. The ships are safe.", "caption"),
      ("", "Day 43: I am the light now.", "quote"),
      ("", "The coast guard found the log open on the desk.\nThe lighthouse had been dark for six weeks.", "caption"),
      ("", "Follow for more Quiet Horror Files.", "endcard")]),

    ("0003_voyagers_silence", "Deep Space Logs", "Voyager's Silence", "STILL CALLING",
     [("DEEP SPACE LOGS", "In 1977 we sent a message to the stars.", "caption"),
      ("", "It carried a map to Earth. A greeting in 55 languages. A heartbeat.", "caption"),
      ("", "We stopped listening for a reply in 1993.", "caption"),
      ("", "It has been answering ever since.", "quote"),
      ("", "We simply built the wrong kind of ears.", "caption"),
      ("", "Follow Deep Space Logs for the next entry.", "endcard")]),

    ("0004_the_map_that_shouldnt_exist", "Unsolved Archive", "The Map That Shouldn't Exist", "DRAWN IN 1513",
     [("UNSOLVED ARCHIVE - FILE 12", "In 1513, a cartographer drew Antarctica.", "caption"),
      ("", "It would not be seen by human eyes for another 300 years.", "caption"),
      ("", "He drew the coastline under the ice. Accurately.", "caption"),
      ("", "He wrote that he copied it from older maps.", "quote"),
      ("", "No one has ever found those maps.", "caption"),
      ("", "Follow Unsolved Archive for the next file.", "endcard")]),

    ("0005_if_the_sun_blinked", "What If Physics", "If the Sun Blinked", "8 MINUTES",
     [("WHAT IF PHYSICS", "What if the Sun vanished for exactly one second?", "caption"),
      ("", "You would not notice for eight minutes.", "caption"),
      ("", "That is how long light takes to cross the gap.", "caption"),
      ("", "Then the sky would go dark - and Earth would keep flying straight.", "quote"),
      ("", "Not falling. Not burning. Just leaving.", "caption"),
      ("", "Follow What If Physics for more.", "endcard")]),

    ("0006_the_second_guest", "Quiet Horror Files", "The Second Guest", "COUNT THEM",
     [("QUIET HORROR FILES", "The hotel had twelve rooms and eleven guests.", "caption"),
      ("", "The night clerk counted the keys every evening. Eleven. Always eleven.", "caption"),
      ("", "On Tuesday he counted twelve.", "caption"),
      ("", "Room 6 had been sealed since 1974.", "quote"),
      ("", "Its key was warm.", "caption"),
      ("", "Follow for more Quiet Horror Files.", "endcard")]),

    ("0007_signal_from_kepler", "Deep Space Logs", "Signal from Kepler", "IT REPEATS",
     [("DEEP SPACE LOGS - ENTRY 4488", "The signal arrived in a clean, patient rhythm.", "caption"),
      ("", "Four pulses. A pause. Four pulses. A pause.", "caption"),
      ("", "Astronomers spent a year deciding it was a pulsar.", "caption"),
      ("", "Then the pause changed. It spelled a number.", "quote"),
      ("", "The number was our own distance from Earth.", "caption"),
      ("", "Follow Deep Space Logs for the next entry.", "endcard")]),

    ("0008_why_nothing_is_empty", "Cosmic Wonders", "Why Nothing Is Empty", "NOTHING ISN'T",
     [("COSMIC WONDERS", "There is no such thing as empty space.", "caption"),
      ("", "Even in a perfect vacuum, particles flicker in and out of existence.", "caption"),
      ("", "They borrow energy, then give it back, faster than time can catch.", "caption"),
      ("", "The void is not silent. It is humming.", "quote"),
      ("", "You are made of the same borrowed energy.", "caption"),
      ("", "Follow Cosmic Wonders for more.", "endcard")]),

    ("0009_the_last_photo", "Unsolved Archive", "The Last Photo", "WHO TOOK IT",
     [("UNSOLVED ARCHIVE - FILE 19", "The hikers were reported missing on a Sunday.", "caption"),
      ("", "Their camera was found on a rock, still working.", "caption"),
      ("", "The final photo showed the trail ahead - and a figure behind them.", "caption"),
      ("", "The figure was wearing the jacket of a man still alive in the city.", "quote"),
      ("", "He had never left his apartment.", "caption"),
      ("", "Follow Unsolved Archive for the next file.", "endcard")]),

    ("0010_if_you_fell_through_earth", "What If Physics", "If You Fell Through Earth", "42 MINUTES",
     [("WHAT IF PHYSICS", "If you fell through a tunnel across the whole Earth...", "caption"),
      ("", "you would accelerate for 42 minutes, then slow to a stop.", "caption"),
      ("", "At the centre you would be weightless - for one perfect instant.", "caption"),
      ("", "Then you would fall all the way back up.", "quote"),
      ("", "And do it again. Forever, if nothing stopped you.", "caption"),
      ("", "Follow What If Physics for more.", "endcard")]),
]


def main() -> int:
    os.makedirs(SPEC_DIR, exist_ok=True)
    written = []
    for slug, series, title, thumb, scenes in PIECES:
        cfg = SERIES[series]
        spec = {
            "slug": slug,
            "title": title,
            "series": series,
            "orientation": "vertical",
            "theme": cfg["theme"],
            "mood": cfg["mood"],
            "voice": cfg["voice"],
            "rate": "+2%",
            "scene_hold": 0.30,
            "scenes": [
                {"kicker": k, "text": t, "style": s,
                 "theme": cfg["theme"], "particles": 50 + (i * 12)}
                for i, (k, t, s) in enumerate(scenes)
            ],
            "packaging": {
                "thumbnail_text": thumb,
                "description": (
                    f"{series} - \"{title}\". Original fiction / original writing produced by "
                    f"AX Viral Content Lab. Written, narrated and rendered in-house with free and "
                    f"open-source tools. No third-party footage, music, or scripts are used.\n\n"
                    + " ".join(cfg["hashtags"])
                ),
                "tags": cfg["tags"],
                "hashtags": cfg["hashtags"],
            },
            "sources": [{
                "note": "Original writing. Structure informed by public market research in research/*.json.",
                "no_reused_material": True,
            }],
        }
        p = os.path.join(SPEC_DIR, f"spec_{slug}.json")
        with open(p, "w") as f:
            json.dump(spec, f, indent=2, ensure_ascii=False)
        written.append(p)
    for p in written:
        print(p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
