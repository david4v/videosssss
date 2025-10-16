from __future__ import annotations

import math
from typing import Optional


def format_bytes(value: Optional[float]) -> str:
    if not value:
        return "-"
    units = ["B", "KB", "MB", "GB", "TB"]
    magnitude = min(int(math.log(value, 1024)) if value > 0 else 0, len(units) - 1)
    scaled = value / math.pow(1024, magnitude)
    return f"{scaled:.2f} {units[magnitude]}"


def format_eta(seconds: Optional[float]) -> str:
    if not seconds:
        return "-"
    seconds = max(0, int(seconds))
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours:d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"
