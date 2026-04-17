"""Centralized greenhouse data loader — loads once, used everywhere."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


_DATA: dict[str, Any] = {}

_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "greenhouse_data.json"


def load_greenhouse_data() -> dict[str, Any]:
    """Load greenhouse_data.json into memory (idempotent).

    Called at app startup via lifespan, and by services at import time
    as a fallback.
    """
    global _DATA
    if not _DATA:
        with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
            _DATA = json.load(f)
    return _DATA


def get_greenhouse_data() -> dict[str, Any]:
    """Return the already-loaded data dict.

    If data hasn't been loaded yet (e.g. during tests), triggers a load.
    """
    if not _DATA:
        return load_greenhouse_data()
    return _DATA
