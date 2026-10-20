#!/usr/bin/env python3
"""Project-wide kill switch for the AX Viral Content Lab.

If a file named STOP exists at the lab root, all content generation halts.
Delete STOP to resume. This is deliberate: it lets the operator stop the lab
without editing code or revoking credentials.
"""
from __future__ import annotations

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STOP_FILE = os.path.join(ROOT, "STOP")


def is_halted() -> bool:
    return os.path.exists(STOP_FILE)


def guard(component: str) -> bool:
    """Return True if work may proceed; print a reason and return False if halted."""
    if is_halted():
        reason = ""
        try:
            with open(STOP_FILE, encoding="utf-8") as f:
                reason = f.read().strip()
        except OSError:
            pass
        print(f"[ax-lab] HALTED: {component} will not run. STOP file present at {STOP_FILE}"
              + (f" ({reason})" if reason else ""))
        return False
    return True
