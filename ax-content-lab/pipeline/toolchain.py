#!/usr/bin/env python3
"""Make the pipeline self-healing across sandbox resets.

A sandbox reset wipes both the system ffmpeg and the pip site-packages, leaving
the pipeline unable to run and with no root to reinstall anything. Importing this
module first guarantees:

  * ffmpeg + ffprobe on PATH (via the `static_ffmpeg` wheel), and
  * the Python deps the pipeline imports.

Installs are quiet and best-effort: if pip is unreachable we still let the caller
proceed so a partial environment fails with a clear error at the point of use.
"""
from __future__ import annotations

import importlib
import shutil
import subprocess
import sys

# module import name -> pip requirement
_PY_DEPS = {
    "numpy": "numpy",
    "PIL": "pillow",
    "edge_tts": "edge-tts",
    "yaml": "pyyaml",
    "static_ffmpeg": "static-ffmpeg",
    "requests": "requests",
}


def _has(module: str) -> bool:
    try:
        importlib.import_module(module)
        return True
    except Exception:  # noqa: BLE001
        return False


def _pip_install(reqs: list[str]) -> bool:
    for args in (["--user"], []):
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "--quiet", "--disable-pip-version-check", *args, *reqs],
                check=True,
                capture_output=True,
                timeout=600,
            )
            return True
        except Exception:  # noqa: BLE001
            continue
    return False


def ensure_python_deps() -> list[str]:
    missing = [req for mod, req in _PY_DEPS.items() if not _has(mod)]
    if missing:
        _pip_install(missing)
        # A --user install lands outside this interpreter's cached sys.path, so
        # the freshly-installed modules stay unimportable until we add it.
        try:
            import site
            user_site = site.getusersitepackages()
            if user_site not in sys.path:
                sys.path.append(user_site)
            importlib.invalidate_caches()
        except Exception:  # noqa: BLE001
            pass
    return [req for mod, req in _PY_DEPS.items() if not _has(mod)]


def ensure_ffmpeg() -> bool:
    if shutil.which("ffmpeg") and shutil.which("ffprobe"):
        return True
    try:
        import static_ffmpeg  # type: ignore
        static_ffmpeg.add_paths()
    except Exception:  # noqa: BLE001
        pass
    return bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))


def ensure() -> bool:
    ensure_python_deps()
    return ensure_ffmpeg()


ensure()
