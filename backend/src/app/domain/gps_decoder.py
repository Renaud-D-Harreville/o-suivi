"""Decode Routechoices PositionArchive (encoded_data) into GPS points.

The encoded_data uses a 6-bit character encoding (Google Encoded Polyline style):
  - Each character represents 6 bits: ``ord(char) - 63``
  - Bit 5 (0x20) is the continuation flag
  - Bits 0–4 (0x1F) carry 5 data bits (LSB first across chunks)
Values are grouped into triplets (timestamp, lat, lon) with zigzag encoding
for signed integers and delta-accumulation across successive points.
"""

from __future__ import annotations

from dataclasses import dataclass

YEAR2010 = 1_262_304_000  # Unix timestamp for 2010-01-01T00:00:00Z


@dataclass(frozen=True, slots=True)
class GpsPoint:
    """A single GPS point decoded from PositionArchive data."""

    timestamp_ms: int  # Unix timestamp in milliseconds
    lat: float
    lon: float


def decode_last_timestamp(encoded_data: str) -> int | None:
    """Return the timestamp (ms) of the last GPS point, or None if no data."""
    points = decode_position_archive(encoded_data)
    if not points:
        return None
    return max(p.timestamp_ms for p in points)


def decode_position_archive(encoded_data: str) -> list[GpsPoint]:
    """Decode a PositionArchive string into a list of GpsPoints.

    Encoding (per character):
    - value = ord(char) - 63
    - bit 5 (0x20): continuation flag (1 = more chunks follow)
    - bits 0-4 (0x1F): 5 data bits, assembled LSB-first

    Triplet semantics:
    - First triplet: all three values are zigzag-encoded (signed)
    - Subsequent triplets: timestamp delta is raw (unsigned),
      lat/lon deltas are zigzag-encoded (signed)
    - Accumulators: each value is added to the running total
    - Final point: timestamp_ms = (YEAR2010 + t) * 1000,
      lat = lat_acc / 1e5, lon = lon_acc / 1e5
    """
    if not encoded_data:
        return []

    pos = 0
    points: list[GpsPoint] = []
    accumulators = [0, 0, 0]  # t, lat_acc, lon_acc
    triplet_index = 0  # 0, 1, 2 within each triplet
    point_count = 0

    while pos < len(encoded_data):
        val, pos = _read_varint(encoded_data, pos)
        if pos < 0:
            break  # malformed data

        # First point: all three values are signed (zigzag)
        # Subsequent points: timestamp delta is unsigned, lat/lon are signed
        if point_count == 0:
            val = _zigzag_decode(val)
        else:
            if triplet_index != 0:
                val = _zigzag_decode(val)

        accumulators[triplet_index] += val
        triplet_index += 1

        if triplet_index == 3:
            triplet_index = 0
            point_count += 1
            timestamp_ms = (YEAR2010 + accumulators[0]) * 1000
            lat = accumulators[1] / 1e5
            lon = accumulators[2] / 1e5
            points.append(GpsPoint(timestamp_ms=timestamp_ms, lat=lat, lon=lon))

    return points


def _read_varint(data: str, pos: int) -> tuple[int, int]:
    """Read a varint from the 6-bit encoded string starting at *pos*.

    Each character carries 5 data bits (bits 0-4) and a continuation flag
    (bit 5).  Data bits are assembled LSB-first.
    Returns ``(value, new_pos)`` or ``(value, -1)`` on truncated input.
    """
    result = 0
    shift = 0
    while pos < len(data):
        chunk = ord(data[pos]) - 63
        pos += 1
        result |= (chunk & 0x1F) << shift
        if (chunk & 0x20) == 0:
            return result, pos
        shift += 5
    return result, -1  # incomplete varint


def _zigzag_decode(val: int) -> int:
    """Decode a ZigZag-encoded signed integer."""
    return (val >> 1) ^ -(val & 1)


