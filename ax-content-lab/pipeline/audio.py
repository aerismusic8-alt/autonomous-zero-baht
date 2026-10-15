#!/usr/bin/env python3
"""Procedural music + audio mixing helpers.

All music is synthesised from scratch with numpy -> 100% original, no licensing
burden, no external assets. Output is 44.1kHz stereo WAV.
"""
from __future__ import annotations
import toolchain  # noqa: F401  (ensures ffmpeg/ffprobe on PATH)

import os
import subprocess
import wave

import numpy as np

SR = 44100

# mood -> (root frequencies, chord intervals, shimmer gain, sub gain)
MOODS = {
    "dark":    ([110.00, 103.83, 116.54, 98.00], [(0, 3, 7), (0, 3, 7), (0, 4, 7), (0, 3, 7)], 0.055, 0.22),
    "mystery": ([98.00, 116.54, 103.83, 123.47], [(0, 3, 7), (0, 4, 7), (0, 3, 7), (0, 3, 6)], 0.070, 0.20),
    "wonder":  ([130.81, 174.61, 196.00, 146.83], [(0, 4, 7), (0, 4, 7), (0, 3, 7), (0, 4, 7)], 0.100, 0.14),
    "calm":    ([130.81, 146.83, 164.81, 174.61], [(0, 4, 7), (0, 3, 7), (0, 4, 7), (0, 4, 7)], 0.080, 0.12),
    "tense":   ([92.50, 98.00, 87.31, 103.83], [(0, 1, 7), (0, 3, 7), (0, 1, 6), (0, 3, 6)], 0.075, 0.24),
}


def _smooth_env(n: int, attack: float, release: float) -> np.ndarray:
    e = np.ones(n)
    na = max(1, int(attack * n))
    nr = max(1, int(release * n))
    e[:na] = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, na))
    e[-nr:] = 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, nr))
    return e


def _osc(freq: float, t: np.ndarray, detune_cents: float = 0.0) -> np.ndarray:
    f = freq * (2 ** (detune_cents / 1200.0))
    return np.sin(2 * np.pi * f * t)


def _chord_bed(freqs, dur, rng):
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for f in freqs:
        # two detuned oscillators + a soft third harmonic
        out += _osc(f, t, -6.0) * 0.5
        out += _osc(f, t, +6.0) * 0.5
        out += _osc(f * 2, t, 0.0) * 0.12
        out += _osc(f * 3, t, 0.0) * 0.05
    # slow tremolo
    lfo = 0.85 + 0.15 * np.sin(2 * np.pi * rng.uniform(0.06, 0.13) * t)
    return out / max(1, len(freqs)) * lfo * _smooth_env(n, 0.28, 0.34)


def _reverb(x: np.ndarray, delays_ms=(41, 67, 97, 131, 173), decay=0.34) -> np.ndarray:
    y = x.copy()
    for d in delays_ms:
        dn = int(d * SR / 1000)
        if dn < len(x):
            y[dn:] += x[:-dn] * decay
    return y / (1 + 0.6 * decay * len(delays_ms) * 0.2)


def generate_music(duration: float, mood: str, out_wav: str, seed: int = 0) -> str:
    """Synthesise an ambient music bed of `duration` seconds."""
    rng = np.random.default_rng(seed)
    roots, intervals, sh_gain, sub_gain = MOODS.get(mood, MOODS["calm"])
    n = int(duration * SR)
    t = np.arange(n) / SR
    mix = np.zeros(n)

    bar = max(4.0, duration / max(2, round(duration / 8)))
    pos = 0.0
    idx = 0
    while pos < duration:
        d = min(bar, duration - pos)
        if d <= 0.05:
            break
        root = roots[idx % len(roots)]
        iv = intervals[idx % len(intervals)]
        freqs = [root * (2 ** (s / 12.0)) for s in iv]
        seg = _chord_bed(freqs, d, rng)
        s0 = int(pos * SR)
        mix[s0:s0 + len(seg)] += seg
        pos += d * 0.92  # slight overlap for smooth crossfade
        idx += 1

    # sub bass drone
    root0 = roots[0] / 2
    mix += _osc(root0, t, 0.0) * sub_gain * (0.8 + 0.2 * np.sin(2 * np.pi * 0.05 * t))

    # shimmer: sparse bell-like tones from a pentatonic set
    penta = [1.0, 9 / 8, 5 / 4, 3 / 2, 5 / 3, 2.0]
    k = 0
    while k < duration:
        f = roots[0] * 4 * penta[rng.integers(0, len(penta))]
        d = rng.uniform(1.2, 3.0)
        nn = int(d * SR)
        tt = np.arange(nn) / SR
        tone = (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * f * 2 * tt))
        tone *= np.exp(-tt / (d * 0.35)) * sh_gain
        s0 = int(k * SR)
        mix[s0:s0 + nn] += tone[:max(0, min(nn, n - s0))]
        k += rng.uniform(1.4, 3.2)

    # airy noise texture
    noise = rng.standard_normal(n)
    kernel = np.ones(220) / 220
    noise = np.convolve(noise, kernel, mode="same")
    mix += noise * 0.012

    mix = _reverb(mix)

    # global fades
    fi = int(1.5 * SR)
    fo = int(2.0 * SR)
    mix[:fi] *= np.linspace(0, 1, fi)
    mix[-fo:] *= np.linspace(1, 0, fo)

    peak = np.max(np.abs(mix)) or 1.0
    mix = mix / peak * 0.85

    # fake stereo width via short haas delay on one channel
    delay = int(0.012 * SR)
    left = mix
    right = np.concatenate([np.zeros(delay), mix[:-delay]]) * 0.92 + mix * 0.08
    stereo = np.stack([left, right], axis=1)

    pcm = (np.clip(stereo, -1, 1) * 32767).astype("<i2")
    with wave.open(out_wav, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    return out_wav


def probe_duration(path: str) -> float:
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", path]).decode().strip()
    return float(out)


def mix_voice_music(voice: str, music: str, out_m4a: str, voice_gain: float = 1.0,
                    music_gain: float = 0.14) -> str:
    """Mix narration over the music bed, normalise loudness."""
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", voice, "-i", music,
        "-filter_complex",
        f"[0:a]volume={voice_gain},highpass=f=80,acompressor=threshold=-18dB:ratio=3:attack=8:release=180[v];"
        f"[1:a]volume={music_gain},lowpass=f=9000[m];"
        f"[v][m]amix=inputs=2:duration=first:dropout_transition=0,"
        f"loudnorm=I=-14:TP=-1.5:LRA=11[out]",
        "-map", "[out]", "-c:a", "aac", "-b:a", "192k", out_m4a], check=True)
    return out_m4a
