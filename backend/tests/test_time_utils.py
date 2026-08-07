"""Unit tests for time_utils — especially date-agnostic calculations."""

from app.domain.time_utils import (
    extract_time_part,
    parse_iso,
    seconds_between,
    time_of_day_seconds,
)


class TestParseIso:
    def test_standard_iso(self):
        dt = parse_iso("2026-08-05T09:30:00")
        assert dt is not None
        assert dt.hour == 9
        assert dt.minute == 30

    def test_with_z_suffix(self):
        dt = parse_iso("2026-08-05T09:30:00Z")
        assert dt is not None

    def test_empty_string(self):
        assert parse_iso("") is None

    def test_invalid(self):
        assert parse_iso("not-a-date") is None


class TestTimeOfDaySeconds:
    def test_midnight(self):
        assert time_of_day_seconds("2026-08-05T00:00:00") == 0

    def test_one_hour(self):
        assert time_of_day_seconds("2026-08-05T01:00:00") == 3600

    def test_mixed(self):
        assert time_of_day_seconds("2026-08-05T10:30:15") == 10 * 3600 + 30 * 60 + 15

    def test_invalid(self):
        assert time_of_day_seconds("invalid") is None


class TestSecondsBetween:
    def test_same_day(self):
        result = seconds_between("2026-08-05T09:00:00", "2026-08-05T10:30:00")
        assert result == 5400  # 1h30m

    def test_different_days_same_time_of_day(self):
        """Key bug fix: dates differ but times are what matters."""
        result = seconds_between("2026-08-05T09:00:00", "2026-08-07T10:30:00")
        assert result == 5400  # 1h30m — NOT 2 days + 1h30m

    def test_different_days_passage_after_departure(self):
        """Departure on day 1, manual beacon edit on day 3 — only time matters."""
        result = seconds_between("2026-08-01T08:00:00", "2026-08-07T09:15:30")
        assert result == 4530  # 1h15m30s

    def test_none_start(self):
        assert seconds_between(None, "2026-08-05T10:30:00") is None

    def test_none_end(self):
        assert seconds_between("2026-08-05T09:00:00", None) is None

    def test_both_none(self):
        assert seconds_between(None, None) is None

    def test_empty_strings(self):
        assert seconds_between("", "2026-08-05T10:30:00") is None

    def test_negative_result(self):
        """End time before start time (e.g. error in data) — returns negative."""
        result = seconds_between("2026-08-05T10:00:00", "2026-08-05T09:00:00")
        assert result == -3600


class TestExtractTimePart:
    def test_normal(self):
        assert extract_time_part("2026-08-05T09:30:15") == "09:30:15"

    def test_different_date_same_time(self):
        assert extract_time_part("2026-08-07T09:30:15") == "09:30:15"

    def test_none(self):
        assert extract_time_part(None) == ""

    def test_empty(self):
        assert extract_time_part("") == ""

    def test_invalid(self):
        assert extract_time_part("not-a-date") == ""

