def to_hms(timestamp: str | None) -> str | None:
    """Normalize any time representation to HH:MM:SS.

    Accepts:
      - ISO format: "2026-08-05T09:30:00" → "09:30:00"
      - Already HH:MM:SS: "09:30:00" → "09:30:00"
      - HH:MM (no seconds): "09:30" → "09:30:00"
      - None or empty → None
    """
    if not timestamp:
        return None
    # ISO format: contains 'T', extract the time part
    if "T" in timestamp:
        time_part = timestamp.split("T")[1]
        # Strip timezone info if present
        for sep in ("+", "Z"):
            if sep in time_part:
                time_part = time_part.split(sep)[0]
        return time_part[:8]
    # Already HH:MM:SS or HH:MM
    if len(timestamp) == 5:
        return timestamp + ":00"
    return timestamp[:8]


def _hms_to_seconds(hms: str) -> int | None:
    """Convert HH:MM:SS string to total seconds since midnight."""
    try:
        parts = hms.split(":")
        if len(parts) < 2:
            return None
        h = int(parts[0])
        m = int(parts[1])
        s = int(parts[2]) if len(parts) > 2 else 0
        return h * 3600 + m * 60 + s
    except (ValueError, IndexError):
        return None


def seconds_between(start: str | None, end: str | None) -> int | None:
    """Return seconds between two time strings (HH:MM:SS or ISO).

    Both inputs are normalized to HH:MM:SS before computation.
    Returns None if either input is missing or unparseable.
    """
    start_hms = to_hms(start)
    end_hms = to_hms(end)
    if not start_hms or not end_hms:
        return None
    start_secs = _hms_to_seconds(start_hms)
    end_secs = _hms_to_seconds(end_hms)
    if start_secs is None or end_secs is None:
        return None
    return end_secs - start_secs


