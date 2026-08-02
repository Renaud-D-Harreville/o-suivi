from datetime import datetime


def parse_iso(timestamp: str) -> datetime | None:
    """Parse an ISO 8601 timestamp string into a datetime."""
    if not timestamp:
        return None
    try:
        return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def seconds_between(start: str | None, end: str | None) -> int | None:
    """Return seconds between two ISO timestamps, or None if either is missing."""
    if not start or not end:
        return None
    dt_start = parse_iso(start)
    dt_end = parse_iso(end)
    if not dt_start or not dt_end:
        return None
    return int((dt_end - dt_start).total_seconds())

