"""Tests for GPS PositionArchive decoder."""

from app.domain.gps_decoder import GpsPoint, _read_varint, _zigzag_decode, decode_position_archive, YEAR2010


# --- Helpers: encode values into the 6-bit character format ---

def _zigzag_encode(n: int) -> int:
    return (n << 1) ^ (n >> 63) if n >= 0 else ((-n) << 1) - 1


def _to_6bit_chars(val: int) -> str:
    """Encode an unsigned integer into 6-bit encoded characters."""
    chars: list[str] = []
    while True:
        chunk = val & 0x1F
        val >>= 5
        if val > 0:
            chunk |= 0x20  # continuation bit
        chars.append(chr(chunk + 63))
        if val == 0:
            break
    return "".join(chars)


def _encode_single_point(t: int, lat_e5: int, lon_e5: int) -> str:
    """Encode a single GPS point (first point, all zigzag-signed)."""
    return (
        _to_6bit_chars(_zigzag_encode(t))
        + _to_6bit_chars(_zigzag_encode(lat_e5))
        + _to_6bit_chars(_zigzag_encode(lon_e5))
    )


def _encode_delta(dt: int, dlat_e5: int, dlon_e5: int) -> str:
    """Encode a delta triplet (timestamp unsigned, lat/lon signed)."""
    return (
        _to_6bit_chars(dt)  # unsigned
        + _to_6bit_chars(_zigzag_encode(dlat_e5))
        + _to_6bit_chars(_zigzag_encode(dlon_e5))
    )


# --- Tests ---


class TestZigzagDecode:
    def test_positive(self) -> None:
        assert _zigzag_decode(0) == 0
        assert _zigzag_decode(2) == 1
        assert _zigzag_decode(4) == 2

    def test_negative(self) -> None:
        assert _zigzag_decode(1) == -1
        assert _zigzag_decode(3) == -2
        assert _zigzag_decode(5) == -3


class TestReadVarint:
    def test_single_char(self) -> None:
        # Value 5 → chunk = 5, no continuation → chr(5 + 63) = chr(68) = 'D'
        val, pos = _read_varint("D", 0)
        assert val == 5
        assert pos == 1

    def test_multi_char(self) -> None:
        # Value 35 = 0b100011 → chunk0 = 00011 | 0x20 = 100011, chunk1 = 00001
        # chr(0b100011 + 63) = chr(98) = 'b',  chr(0b00001 + 63) = chr(64) = '@'
        val, pos = _read_varint("b@", 0)
        assert val == 35
        assert pos == 2

    def test_with_offset(self) -> None:
        val, pos = _read_varint("XD", 1)
        assert val == 5
        assert pos == 2


class TestDecodePositionArchive:
    def test_empty_string(self) -> None:
        assert decode_position_archive("") == []

    def test_single_point(self) -> None:
        """Manually construct a single-point PositionArchive and verify decoding."""
        encoded = _encode_single_point(100, 4612345, 612345)
        points = decode_position_archive(encoded)

        assert len(points) == 1
        assert points[0].timestamp_ms == (YEAR2010 + 100) * 1000
        assert abs(points[0].lat - 46.12345) < 1e-6
        assert abs(points[0].lon - 6.12345) < 1e-6

    def test_two_points(self) -> None:
        """Two points: second uses unsigned timestamp delta, signed lat/lon deltas."""
        encoded = _encode_single_point(100, 4612345, 612345)
        encoded += _encode_delta(60, -100, 200)
        points = decode_position_archive(encoded)

        assert len(points) == 2
        # Point 1
        assert points[0].timestamp_ms == (YEAR2010 + 100) * 1000
        assert abs(points[0].lat - 46.12345) < 1e-6
        assert abs(points[0].lon - 6.12345) < 1e-6
        # Point 2
        assert points[1].timestamp_ms == (YEAR2010 + 160) * 1000
        assert abs(points[1].lat - (4612345 - 100) / 1e5) < 1e-6
        assert abs(points[1].lon - (612345 + 200) / 1e5) < 1e-6

    def test_real_data_first_point(self) -> None:
        """Verify decoding of a known prefix from real Routechoices data.

        The first 6 chars 'ksgwf^' encode the timestamp of the first point.
        We test that the first decoded point produces plausible Grenoble-area coordinates.
        """
        # Minimal hand-verified snippet: first triplet from the real API-test event.
        # Timestamp zigzag(524288006) → encodes to 'ksgwf^'
        # Lat zigzag(4521700) → 'gm~rG'
        # Lon zigzag(579251) → 'ejjb@'
        snippet = "ksgwf^gm~rGejjb@"
        points = decode_position_archive(snippet)

        assert len(points) == 1
        assert abs(points[0].lat - 45.21700) < 0.001
        assert abs(points[0].lon - 5.79251) < 0.001


