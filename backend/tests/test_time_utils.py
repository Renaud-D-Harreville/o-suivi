"""Unit tests for time_utils — HH:MM:SS based calculations."""

from app.domain.time_utils import (
    _hms_to_seconds,
    seconds_between,
    to_hms,
)


class TestToHms:
    def test_iso_format(self):
        assert to_hms("2026-08-05T09:30:15") == "09:30:15"

    def test_iso_with_timezone(self):
        assert to_hms("2026-08-05T09:30:15+02:00") == "09:30:15"

    def test_iso_with_z(self):
        assert to_hms("2026-08-05T09:30:15Z") == "09:30:15"

    def test_already_hms(self):
        assert to_hms("09:30:15") == "09:30:15"

    def test_hm_no_seconds(self):
        assert to_hms("09:30") == "09:30:00"

    def test_none(self):
        assert to_hms(None) is None

    def test_empty(self):
        assert to_hms("") is None


class TestHmsToSeconds:
    def test_midnight(self):
        assert _hms_to_seconds("00:00:00") == 0

    def test_one_hour(self):
        assert _hms_to_seconds("01:00:00") == 3600

    def test_mixed(self):
        assert _hms_to_seconds("10:30:15") == 10 * 3600 + 30 * 60 + 15

    def test_invalid(self):
        assert _hms_to_seconds("invalid") is None


class TestSecondsBetween:
    def test_hms_same_format(self):
        result = seconds_between("09:00:00", "10:30:00")
        assert result == 5400  # 1h30m

    def test_iso_format_both(self):
        """Backward compat: still works with ISO inputs."""
        result = seconds_between("2026-08-05T09:00:00", "2026-08-07T10:30:00")
        assert result == 5400  # 1h30m — ignores dates

    def test_mixed_iso_and_hms(self):
        """Mixed formats: ISO start, HH:MM:SS end."""
        result = seconds_between("2026-08-05T09:00:00", "10:30:00")
        assert result == 5400

    def test_none_start(self):
        assert seconds_between(None, "10:30:00") is None

    def test_none_end(self):
        assert seconds_between("09:00:00", None) is None

    def test_both_none(self):
        assert seconds_between(None, None) is None

    def test_empty_strings(self):
        assert seconds_between("", "10:30:00") is None

    def test_negative_result(self):
        result = seconds_between("10:00:00", "09:00:00")
        assert result == -3600


