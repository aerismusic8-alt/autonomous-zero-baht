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

    ("0011_the_probe_that_came_back", "Deep Space Logs", "The Probe That Came Back", "IT RECORDED US",
     [("DEEP SPACE LOGS - ENTRY 5120", "We launched it in 1979 and forgot it by 1990.", "caption"),
      ("", "Last month, it came back.", "caption"),
      ("", "Its data core held one file: forty years of audio.", "caption"),
      ("", "The first four minutes are the launch. You can hear the engineers cheering.", "quote"),
      ("", "The last four minutes are the same cheering. From the other side.", "caption"),
      ("", "Follow Deep Space Logs for the next entry.", "endcard")]),

    ("0012_six_minutes_of_silence", "Deep Space Logs", "Six Minutes of Silence", "MISSING TIME",
     [("DEEP SPACE LOGS - ENTRY 5301", "The Mars crew went quiet for six minutes.", "caption"),
      ("", "Every system logged it. Every camera missed it.", "caption"),
      ("", "They woke up on schedule, in the right seats, wearing the right suits.", "caption"),
      ("", "But all four of them were soaking wet.", "quote"),
      ("", "There has never been liquid water on that part of Mars.", "caption"),
      ("", "Follow Deep Space Logs for the next entry.", "endcard")]),

    ("0013_the_long_orbit", "Deep Space Logs", "The Long Orbit", "STILL ORBITING",
     [("DEEP SPACE LOGS - ENTRY 5477", "She woke from cryo expecting a busy station.", "caption"),
      ("", "The station was still there. Still orbiting. Still in perfect repair.", "caption"),
      ("", "The logs ran without a single gap for two hundred years.", "caption"),
      ("", "The last entry was written in her own handwriting.", "quote"),
      ("", "It said: do not wake up before you read this.", "caption"),
      ("", "Follow Deep Space Logs for the next entry.", "endcard")]),

    ("0014_duplicate_transmission", "Deep Space Logs", "Duplicate Transmission", "TWO OF THE SAME",
     [("DEEP SPACE LOGS - ENTRY 5610", "Two identical signals arrived within a second of each other.", "caption"),
      ("", "Same frequency. Same length. Same content.", "caption"),
      ("", "One came from a star forty light years away.", "caption"),
      ("", "The other came from the far side of our own Moon.", "quote"),
      ("", "The Moon signal arrived first.", "caption"),
      ("", "Follow Deep Space Logs for the next entry.", "endcard")]),

    ("0015_the_house_that_counts", "Quiet Horror Files", "The House That Counts", "FIVE ROOMS",
     [("QUIET HORROR FILES", "The house had five rooms. Everyone agreed on that.", "caption"),
      ("", "Five rooms, one hall, one front door.", "caption"),
      ("", "But every night, someone walked past the bedroom twice.", "caption"),
      ("", "The floorboards counted six sets of footsteps.", "quote"),
      ("", "The house had five rooms. It always had six visitors.", "caption"),
      ("", "Follow for more Quiet Horror Files.", "endcard")]),

    ("0016_the_note_in_the_fridge", "Quiet Horror Files", "The Note in the Fridge", "IT KNOWS",
     [("QUIET HORROR FILES", "She lived alone and kept a tidy fridge.", "caption"),
      ("", "On Monday there was a note on the milk: you forgot the eggs.", "caption"),
      ("", "She had forgotten the eggs. She laughed it off.", "caption"),
      ("", "On Friday the note said: you are reading this on Friday.", "quote"),
      ("", "It was the only note she had not written herself.", "caption"),
      ("", "Follow for more Quiet Horror Files.", "endcard")]),

    ("0017_the_three_am_train", "Quiet Horror Files", "The 3 AM Train", "CLOSED 1957",
     [("QUIET HORROR FILES", "The station closed in 1957. The tracks were lifted in 1962.", "caption"),
      ("", "But at 3 AM, the platform lights still come on.", "caption"),
      ("", "The timetable board still shows one departure.", "caption"),
      ("", "It has no destination listed. Only a time.", "quote"),
      ("", "3 AM. Every night. For sixty years.", "caption"),
      ("", "Follow for more Quiet Horror Files.", "endcard")]),

    ("0018_the_extra_shadow", "Quiet Horror Files", "The Extra Shadow", "COUNT THEM",
     [("QUIET HORROR FILES", "The photograph was taken at noon, in full sun.", "caption"),
      ("", "Three children stood in a row on the beach.", "caption"),
      ("", "Three small shadows stretched out in front of them.", "caption"),
      ("", "And one more, behind them, facing the wrong way.", "quote"),
      ("", "None of them had anyone standing behind them.", "caption"),
      ("", "Follow for more Quiet Horror Files.", "endcard")]),

    ("0019_the_speed_of_falling", "Cosmic Wonders", "The Speed of Falling", "NOT A FORCE",
     [("COSMIC WONDERS", "Gravity is not pulling you down.", "caption"),
      ("", "You are not being pulled at all.", "caption"),
      ("", "You are falling - and the ground is rushing up to meet you.", "caption"),
      ("", "A feather and a hammer fall at the same speed. There is no pull.", "quote"),
      ("", "There is only the curve of space, bending toward the Earth.", "caption"),
      ("", "Follow Cosmic Wonders for more.", "endcard")]),

    ("0020_why_stars_die_twice", "Cosmic Wonders", "Why Stars Die Twice", "TWICE",
     [("COSMIC WONDERS", "A massive star does not simply die.", "caption"),
      ("", "It collapses, then explodes, then collapses again.", "caption"),
      ("", "The first death is silent. The second one outshines a galaxy.", "caption"),
      ("", "For a few weeks, it is brighter than every star in the sky combined.", "quote"),
      ("", "Then it leaves behind a single spoonful weighing a billion tonnes.", "caption"),
      ("", "Follow Cosmic Wonders for more.", "endcard")]),

    ("0021_the_coldest_place", "Cosmic Wonders", "The Coldest Place", "COLDER THAN SPACE",
     [("COSMIC WONDERS", "The coldest place we have ever found is not in deep space.", "caption"),
      ("", "It is a cloud of gas 5,000 light years away, called the Boomerang Nebula.", "caption"),
      ("", "It sits at one degree above absolute zero.", "caption"),
      ("", "That is colder than the empty space around it.", "quote"),
      ("", "It is colder than the light left over from the Big Bang.", "caption"),
      ("", "Follow Cosmic Wonders for more.", "endcard")]),

    ("0022_the_sound_of_a_black_hole", "Cosmic Wonders", "The Sound of a Black Hole", "IT HUMS",
     [("COSMIC WONDERS", "Black holes are silent. Space carries no air for sound.", "caption"),
      ("", "But the gas around them is not silent.", "caption"),
      ("", "It ripples in pressure waves you could hear if your ears were light years wide.", "caption"),
      ("", "One of them hums fifty-seven octaves below middle C.", "quote"),
      ("", "It has been humming the same note for two billion years.", "caption"),
      ("", "Follow Cosmic Wonders for more.", "endcard")]),

    ("0023_the_vanished_village", "Unsolved Archive", "The Vanished Village", "300 PEOPLE",
     [("UNSOLVED ARCHIVE - FILE 27", "In 1930, a fur trapper reached a village of three hundred people.", "caption"),
      ("", "Every door was open. Every stove was cold but full.", "caption"),
      ("", "Meals sat half-eaten on the tables.", "caption"),
      ("", "The sled dogs were still tethered. They had not been fed for days.", "quote"),
      ("", "No one has ever explained where three hundred people went.", "caption"),
      ("", "Follow Unsolved Archive for the next file.", "endcard")]),

    ("0024_the_man_who_never_slept", "Unsolved Archive", "The Man Who Never Slept", "NEVER",
     [("UNSOLVED ARCHIVE - FILE 33", "He was admitted complaining that he could not sleep.", "caption"),
      ("", "Doctors watched him for weeks. He never closed his eyes.", "caption"),
      ("", "His body was healthy. His mind stayed sharp.", "caption"),
      ("", "He claimed he had not slept since a fever as a boy.", "quote"),
      ("", "No one ever found a cause - or a reason to disbelieve him.", "caption"),
      ("", "Follow Unsolved Archive for the next file.", "endcard")]),

    ("0025_the_tape_from_room_three", "Unsolved Archive", "The Tape from Room 3", "WHO SPOKE",
     [("UNSOLVED ARCHIVE - FILE 41", "A recorder was left running in an empty room overnight.", "caption"),
      ("", "The tape held nine hours of silence.", "caption"),
      ("", "Then, at 4:07, a calm voice said one sentence.", "caption"),
      ("", "It named the investigator who would later take the case.", "quote"),
      ("", "That investigator was eleven years old at the time.", "caption"),
      ("", "Follow Unsolved Archive for the next file.", "endcard")]),

    ("0026_the_second_landing", "Unsolved Archive", "The Second Landing", "IT LANDED TWICE",
     [("UNSOLVED ARCHIVE - FILE 48", "The flight landed safely and everyone disembarked.", "caption"),
      ("", "The log shows the same flight landing twice, forty minutes apart.", "caption"),
      ("", "Same airport. Same gate. Same passengers.", "caption"),
      ("", "The second entry lists one extra passenger, unnamed.", "quote"),
      ("", "The aircraft has since flown thousands of times without incident.", "caption"),
      ("", "Follow Unsolved Archive for the next file.", "endcard")]),

    ("0027_if_you_stopped_time", "What If Physics", "If You Stopped Time", "ONE SECOND",
     [("WHAT IF PHYSICS", "What if time stopped - but only for you?", "caption"),
      ("", "Everyone would freeze mid-step. The world would hold its breath.", "caption"),
      ("", "You could walk anywhere. Move anything.", "caption"),
      ("", "But light is carried by time. Without it, you would see nothing at all.", "quote"),
      ("", "You would be awake, alone, in perfect darkness, forever.", "caption"),
      ("", "Follow What If Physics for more.", "endcard")]),

    ("0028_if_light_was_slow", "What If Physics", "If Light Was Slow", "WALKING PACE",
     [("WHAT IF PHYSICS", "Light travels 300,000 kilometres every second.", "caption"),
      ("", "Now slow it down to walking pace.", "caption"),
      ("", "The Sun would go dark, and you would keep seeing it for eight years.", "caption"),
      ("", "You would look at a mirror and see your own face days later.", "quote"),
      ("", "Every star you see tonight would be a memory.", "caption"),
      ("", "Follow What If Physics for more.", "endcard")]),

    ("0029_if_the_ocean_drained", "What If Physics", "If the Ocean Drained", "A NEW WORLD",
     [("WHAT IF PHYSICS", "If the oceans drained away tomorrow...", "caption"),
      ("", "the seafloor would become the largest landscape on Earth.", "caption"),
      ("", "Mountain ranges taller than the Himalayas would rise into open air.", "caption"),
      ("", "Under the water, we have mapped less than a quarter of it.", "quote"),
      ("", "We would be looking at a continent nobody has ever seen.", "caption"),
      ("", "Follow What If Physics for more.", "endcard")]),

    ("0030_if_you_could_see_radio", "What If Physics", "If You Could See Radio", "BLINDING",
     [("WHAT IF PHYSICS", "Every phone call, every broadcast, every satellite is passing through you.", "caption"),
      ("", "If your eyes could see radio waves, the sky would never be dark.", "caption"),
      ("", "It would glow with thousands of overlapping signals.", "caption"),
      ("", "Our own transmissions would outshine every star.", "quote"),
      ("", "We have already filled the sky with light we cannot see.", "caption"),
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
