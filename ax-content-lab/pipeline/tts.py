#!/usr/bin/env python3
"""Narration via edge-tts (free Microsoft neural voices, no API key)."""
from __future__ import annotations

import asyncio
import os

import edge_tts

# Curated free neural voices. Rotate voices for variety / A-B testing.
VOICES = {
    "male_documentary": "en-US-GuyNeural",
    "male_calm": "en-US-ChristopherNeural",
    "male_warm": "en-US-EricNeural",
    "female_warm": "en-US-AriaNeural",
    "female_calm": "en-US-JennyNeural",
    "female_news": "en-US-MichelleNeural",
    "male_uk": "en-GB-RyanNeural",
    "female_uk": "en-GB-SoniaNeural",
}


async def _synth(text: str, voice: str, rate: str, out: str) -> None:
    comm = edge_tts.Communicate(text, voice, rate=rate)
    await comm.save(out)


def speak(text: str, voice_key: str, out_path: str, rate: str = "+0%") -> str:
    voice = VOICES.get(voice_key, voice_key)
    asyncio.run(_synth(text, voice, rate, out_path))
    if not os.path.exists(out_path) or os.path.getsize(out_path) < 500:
        raise RuntimeError(f"TTS produced no audio for voice={voice}")
    return out_path
