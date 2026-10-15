#!/usr/bin/env python3
"""Ensure ffmpeg/ffprobe are on PATH.

Sandboxes reset and wipe the system ffmpeg; there is no root to apt-get it back.
`static_ffmpeg` ships a full ffmpeg+ffprobe pair as a pip wheel and can add them
to PATH, so importing this module first makes the pipeline self-healing.
"""
from __future__ import annotations

import shutil


def ensure() -> bool:
    if shutil.which("ffmpeg") and shutil.which("ffprobe"):
        return True
    try:
        import static_ffmpeg  # type: ignore
        static_ffmpeg.add_paths()
    except Exception:  # noqa: BLE001
        pass
    return bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))


ensure()
