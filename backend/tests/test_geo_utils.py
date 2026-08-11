"""Tests for geographic utility functions."""

from app.domain.geo_utils import haversine_distance, parse_coordinates


class TestHaversineDistance:
    def test_same_point(self) -> None:
        assert haversine_distance(46.0, 6.0, 46.0, 6.0) == 0.0

    def test_known_distance(self) -> None:
        # Paris (48.8566, 2.3522) to Lyon (45.7640, 4.8357) ≈ 392 km
        dist = haversine_distance(48.8566, 2.3522, 45.7640, 4.8357)
        assert 390_000 < dist < 395_000

    def test_short_distance(self) -> None:
        # Two points ~11m apart (0.0001° lat ≈ 11.1m)
        dist = haversine_distance(46.0, 6.0, 46.0001, 6.0)
        assert 10 < dist < 12

    def test_within_25m(self) -> None:
        # ~22m apart → within 25m radius
        dist = haversine_distance(46.0, 6.0, 46.0002, 6.0)
        assert dist < 25

    def test_outside_25m(self) -> None:
        # ~33m apart → outside 25m radius
        dist = haversine_distance(46.0, 6.0, 46.0003, 6.0)
        assert dist > 25


class TestParseCoordinates:
    def test_valid(self) -> None:
        assert parse_coordinates("46.12345,6.12345") == (46.12345, 6.12345)

    def test_valid_with_spaces(self) -> None:
        assert parse_coordinates("46.12345, 6.12345") == (46.12345, 6.12345)

    def test_negative(self) -> None:
        assert parse_coordinates("-33.8688,151.2093") == (-33.8688, 151.2093)

    def test_invalid_format(self) -> None:
        assert parse_coordinates("not-coords") is None

    def test_empty(self) -> None:
        assert parse_coordinates("") is None

    def test_three_parts(self) -> None:
        assert parse_coordinates("1,2,3") is None

