from datetime import datetime


def parse_iso(timestamp: str) -> datetime | None:
    """Parse an ISO 8601 timestamp string into a datetime."""
    if not timestamp:
        return None
    try:
        return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def time_of_day_seconds(timestamp: str) -> int | None:
    """Extract the time-of-day component from an ISO timestamp as total seconds.

    Ignores the date part entirely — only uses HH:MM:SS.
    """
    dt = parse_iso(timestamp)
    if dt is None:
        return None
    return dt.hour * 3600 + dt.minute * 60 + dt.second


def seconds_between(start: str | None, end: str | None) -> int | None:
    """Return seconds between two timestamps using time-of-day only.

    Ignores the date component to avoid mismatches when timestamps
    were recorded on different days (e.g. manual edits after the event).
    """
    if not start or not end:
        return None
    start_secs = time_of_day_seconds(start)
    end_secs = time_of_day_seconds(end)
    if start_secs is None or end_secs is None:
        return None
    return end_secs - start_secs


def extract_time_part(timestamp: str | None) -> str:
    """Extract the HH:MM:SS portion from an ISO timestamp for ordering purposes."""
    if not timestamp:
        return ""
    dt = parse_iso(timestamp)
    if dt is None:
        return ""
    return f"{dt.hour:02d}:{dt.minute:02d}:{dt.second:02d}"

