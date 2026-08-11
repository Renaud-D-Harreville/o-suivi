"""Geographic utility functions for GPS distance and coordinate parsing."""

from __future__ import annotations

import math

_EARTH_RADIUS_M = 6_371_000  # Earth radius in meters


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return the distance in meters between two GPS coordinates (Haversine formula)."""
    lat1_r, lon1_r = math.radians(lat1), math.radians(lon1)
    lat2_r, lon2_r = math.radians(lat2), math.radians(lon2)

    dlat = lat2_r - lat1_r
    dlon = lon2_r - lon1_r

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return _EARTH_RADIUS_M * c


def parse_coordinates(coordinates: str) -> tuple[float, float] | None:
    """Parse a 'lat,lon' string into (lat, lon). Returns None on failure."""
    try:
        parts = coordinates.split(",")
        if len(parts) != 2:
            return None
        return float(parts[0].strip()), float(parts[1].strip())
    except (ValueError, AttributeError):
        return None

