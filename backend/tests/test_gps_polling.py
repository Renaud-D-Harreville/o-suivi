"""Tests for GPS polling service — beacon detection logic."""

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from app.domain.gps_decoder import YEAR2010
from app.repositories.event_repository import EventRepository
from app.repositories.log_repository import LogRepository
from app.schemas.events import EventDetail, EventRegistration
from app.schemas.routechoices import RoutechoicesCompetitorRaw, RoutechoicesEventDataRaw
from app.services.gps_polling_service import GpsPollingService
from app.services.routechoices_service import RoutechoicesService


# --- Helpers: 6-bit character encoding (same as Routechoices PositionArchive) ---

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


def _encode_two_points(
    t1: int, lat1_e5: int, lon1_e5: int,
    dt: int, dlat_e5: int, dlon_e5: int,
) -> str:
    """Encode two GPS points into 6-bit PositionArchive format."""
    return (
        _encode_single_point(t1, lat1_e5, lon1_e5)
        + _to_6bit_chars(dt)  # unsigned timestamp delta
        + _to_6bit_chars(_zigzag_encode(dlat_e5))
        + _to_6bit_chars(_zigzag_encode(dlon_e5))
    )


def _make_event(
    event_id: str = "evt1",
    beacons: list[dict] | None = None,
    courses: list[dict] | None = None,
    registrations: list[dict] | None = None,
) -> dict:
    """Create a minimal event dict for testing."""
    return {
        "id": event_id,
        "name": "Test Event",
        "date": None,
        "template_id": None,
        "first_start_time": "08:00",
        "routechoices_url": None,
        "routechoices_event_id": "rc_evt_1",
        "gps_polling_enabled": True,
        "start_mode": None,
        "beacons": beacons or [],
        "courses": courses or [],
        "time_gates": [],
        "registrations": registrations or [],
    }


def _setup_event(events_dir: Path, event_data: dict) -> None:
    """Write an event.json file to the test data directory."""
    event_dir = events_dir / event_data["id"]
    event_dir.mkdir(parents=True, exist_ok=True)
    (event_dir / "logs").mkdir(exist_ok=True)
    beacon_map = {b["id"]: b for b in event_data.get("beacons", [])}
    enriched_courses = []
    for c in event_data.get("courses", []):
        enriched_courses.append({
            "number": c["number"],
            "beacons": [beacon_map[bid] for bid in c.get("beacons", []) if bid in beacon_map],
        })
    raw = dict(event_data)
    raw["courses"] = [{"number": c["number"], "beacons": c.get("beacons", [])} for c in event_data.get("courses", [])]
    with (event_dir / "event.json").open("w") as f:
        json.dump(raw, f, indent=2)


# --- Tests ---


class TestGpsPollingNormalBeacon:
    """GPS polling detects normal beacon passages."""

    @pytest.mark.asyncio
    async def test_writes_checkpoint_edit_when_within_radius(self, tmp_path: Path) -> None:
        """A GPS point within 25m of a beacon should write a checkpoint_edit log."""
        # Beacon at exactly (46.0, 6.0)
        beacon = {"id": 31, "number": 1, "tag": "B1", "is_ph": False, "code": "AB", "coordinates": "46.0,6.0"}
        reg = {"user_id": "u1", "course_number": 1, "routechoices_short_name": "alice"}
        event_data = _make_event(
            beacons=[beacon],
            courses=[{"number": 1, "beacons": [31]}],
            registrations=[reg],
        )

        # GPS point at (46.0001, 6.0) ≈ 11m from beacon → within 25m
        encoded = _encode_single_point(1000, 4600010, 600000)

        events_dir = tmp_path / "events"
        _setup_event(events_dir, event_data)

        event_repo = EventRepository()
        event_repo._events_dir = events_dir

        log_repo = LogRepository()
        log_repo._events_dir = events_dir

        rc_service = MagicMock(spec=RoutechoicesService)
        rc_service.resolve_event_id.return_value = "rc_evt_1"
        rc_service.fetch_event_payload.return_value = RoutechoicesEventDataRaw(
            competitors=[
                RoutechoicesCompetitorRaw(id="c1", encoded_data=encoded, short_name="Alice"),
            ]
        )

        service = GpsPollingService(events=event_repo, logs=log_repo, rc=rc_service)
        await service.poll_once()

        # Verify a log was written
        log_file = events_dir / "evt1" / "logs" / "u1.json"
        assert log_file.exists()
        with log_file.open() as f:
            logs = json.load(f)
        assert len(logs) == 1
        assert logs[0]["log_type"] == "checkpoint_edit"
        assert logs[0]["data"]["sequence"] == 1
        assert logs[0]["data"]["code"] == "AB"
        assert logs[0]["metadata"]["author_id"] == "gps"

    @pytest.mark.asyncio
    async def test_no_write_when_outside_radius(self, tmp_path: Path) -> None:
        """A GPS point >25m from a beacon should NOT write any log."""
        beacon = {"id": 31, "number": 1, "tag": "B1", "is_ph": False, "code": "AB", "coordinates": "46.0,6.0"}
        reg = {"user_id": "u1", "course_number": 1, "routechoices_short_name": "bob"}
        event_data = _make_event(
            beacons=[beacon],
            courses=[{"number": 1, "beacons": [31]}],
            registrations=[reg],
        )

        # GPS point at (46.001, 6.0) ≈ 111m from beacon → outside 25m
        encoded = _encode_single_point(1000, 4600100, 600000)

        events_dir = tmp_path / "events"
        _setup_event(events_dir, event_data)

        event_repo = EventRepository()
        event_repo._events_dir = events_dir

        log_repo = LogRepository()
        log_repo._events_dir = events_dir

        rc_service = MagicMock(spec=RoutechoicesService)
        rc_service.resolve_event_id.return_value = "rc_evt_1"
        rc_service.fetch_event_payload.return_value = RoutechoicesEventDataRaw(
            competitors=[
                RoutechoicesCompetitorRaw(id="c1", encoded_data=encoded, short_name="bob"),
            ]
        )

        service = GpsPollingService(events=event_repo, logs=log_repo, rc=rc_service)
        await service.poll_once()

        log_file = events_dir / "evt1" / "logs" / "u1.json"
        assert not log_file.exists()

    @pytest.mark.asyncio
    async def test_no_overwrite_existing_passage_time(self, tmp_path: Path) -> None:
        """If a checkpoint already has a passage_time, GPS should NOT overwrite it."""
        beacon = {"id": 31, "number": 1, "tag": "B1", "is_ph": False, "code": "AB", "coordinates": "46.0,6.0"}
        reg = {"user_id": "u1", "course_number": 1, "routechoices_short_name": "charlie"}
        event_data = _make_event(
            beacons=[beacon],
            courses=[{"number": 1, "beacons": [31]}],
            registrations=[reg],
        )

        events_dir = tmp_path / "events"
        _setup_event(events_dir, event_data)

        # Pre-existing log with passage_time
        existing_log = [{
            "log_type": "checkpoint_edit",
            "metadata": {
                "creation_date": "2026-08-01T09:00:00",
                "received_at": "2026-08-01T09:00:01",
                "author_id": "manual",
            },
            "data": {"sequence": 1, "code": "AB", "passage_time": "09:00:00"},
        }]
        log_dir = events_dir / "evt1" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        with (log_dir / "u1.json").open("w") as f:
            json.dump(existing_log, f)

        # GPS point right on top of beacon
        encoded = _encode_single_point(1000, 4600000, 600000)

        event_repo = EventRepository()
        event_repo._events_dir = events_dir

        log_repo = LogRepository()
        log_repo._events_dir = events_dir

        rc_service = MagicMock(spec=RoutechoicesService)
        rc_service.resolve_event_id.return_value = "rc_evt_1"
        rc_service.fetch_event_payload.return_value = RoutechoicesEventDataRaw(
            competitors=[
                RoutechoicesCompetitorRaw(id="c1", encoded_data=encoded, short_name="Charlie"),
            ]
        )

        service = GpsPollingService(events=event_repo, logs=log_repo, rc=rc_service)
        await service.poll_once()

        # Should still have only 1 log (the original)
        with (log_dir / "u1.json").open() as f:
            logs = json.load(f)
        assert len(logs) == 1


class TestGpsPollingPhBeacon:
    """GPS polling handles PH beacon entry/exit correctly."""

    @pytest.mark.asyncio
    async def test_writes_ph_arrival_on_entry(self, tmp_path: Path) -> None:
        """First GPS point ≤ 25m of a PH beacon → ph_arrival_edit."""
        beacon = {"id": 31, "number": 1, "tag": "PH1", "is_ph": True, "code": "PH", "coordinates": "46.0,6.0"}
        reg = {"user_id": "u1", "course_number": 1, "routechoices_short_name": "dana"}
        event_data = _make_event(
            beacons=[beacon],
            courses=[{"number": 1, "beacons": [31]}],
            registrations=[reg],
        )

        # GPS point near beacon
        encoded = _encode_single_point(1000, 4600010, 600000)

        events_dir = tmp_path / "events"
        _setup_event(events_dir, event_data)

        event_repo = EventRepository()
        event_repo._events_dir = events_dir

        log_repo = LogRepository()
        log_repo._events_dir = events_dir

        rc_service = MagicMock(spec=RoutechoicesService)
        rc_service.resolve_event_id.return_value = "rc_evt_1"
        rc_service.fetch_event_payload.return_value = RoutechoicesEventDataRaw(
            competitors=[
                RoutechoicesCompetitorRaw(id="c1", encoded_data=encoded, short_name="dana"),
            ]
        )

        service = GpsPollingService(events=event_repo, logs=log_repo, rc=rc_service)
        await service.poll_once()

        log_file = events_dir / "evt1" / "logs" / "u1.json"
        assert log_file.exists()
        with log_file.open() as f:
            logs = json.load(f)
        assert len(logs) == 1
        assert logs[0]["log_type"] == "ph_arrival_edit"
        assert logs[0]["data"]["sequence"] == 1
        assert logs[0]["metadata"]["author_id"] == "gps"

    @pytest.mark.asyncio
    async def test_writes_checkpoint_on_exit(self, tmp_path: Path) -> None:
        """After PH arrival exists, first GPS point >25m → checkpoint_edit."""
        beacon = {"id": 31, "number": 1, "tag": "PH1", "is_ph": True, "code": "PH", "coordinates": "46.0,6.0"}
        reg = {"user_id": "u1", "course_number": 1, "routechoices_short_name": "eve"}
        event_data = _make_event(
            beacons=[beacon],
            courses=[{"number": 1, "beacons": [31]}],
            registrations=[reg],
        )

        events_dir = tmp_path / "events"
        _setup_event(events_dir, event_data)

        # Pre-existing ph_arrival_edit log
        existing_log = [{
            "log_type": "ph_arrival_edit",
            "metadata": {
                "creation_date": "2026-08-01T09:00:00",
                "received_at": "2026-08-01T09:00:01",
                "author_id": "gps",
            },
            "data": {"sequence": 1, "passage_time": "09:00:00"},
        }]
        log_dir = events_dir / "evt1" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        with (log_dir / "u1.json").open("w") as f:
            json.dump(existing_log, f)

        # Two GPS points: first inside (entry), then outside (exit)
        encoded = _encode_two_points(
            t1=1000, lat1_e5=4600001, lon1_e5=600000,    # ≈ 1m → inside
            dt=60, dlat_e5=50, dlon_e5=0,                 # → 46.00051 ≈ 56m → outside
        )

        event_repo = EventRepository()
        event_repo._events_dir = events_dir

        log_repo = LogRepository()
        log_repo._events_dir = events_dir

        rc_service = MagicMock(spec=RoutechoicesService)
        rc_service.resolve_event_id.return_value = "rc_evt_1"
        rc_service.fetch_event_payload.return_value = RoutechoicesEventDataRaw(
            competitors=[
                RoutechoicesCompetitorRaw(id="c1", encoded_data=encoded, short_name="eve"),
            ]
        )

        service = GpsPollingService(events=event_repo, logs=log_repo, rc=rc_service)
        await service.poll_once()

        with (log_dir / "u1.json").open() as f:
            logs = json.load(f)
        assert len(logs) == 2
        assert logs[0]["log_type"] == "ph_arrival_edit"
        assert logs[1]["log_type"] == "checkpoint_edit"
        assert logs[1]["data"]["code"] == "PH"
        assert logs[1]["data"]["sequence"] == 1


class TestGpsPollingMatching:
    """Matching by short_name is case-insensitive."""

    @pytest.mark.asyncio
    async def test_case_insensitive_matching(self, tmp_path: Path) -> None:
        beacon = {"id": 31, "number": 1, "tag": "B1", "is_ph": False, "code": "AB", "coordinates": "46.0,6.0"}
        reg = {"user_id": "u1", "course_number": 1, "routechoices_short_name": "Alice"}
        event_data = _make_event(
            beacons=[beacon],
            courses=[{"number": 1, "beacons": [31]}],
            registrations=[reg],
        )

        # GPS point on beacon
        encoded = _encode_single_point(1000, 4600000, 600000)

        events_dir = tmp_path / "events"
        _setup_event(events_dir, event_data)

        event_repo = EventRepository()
        event_repo._events_dir = events_dir

        log_repo = LogRepository()
        log_repo._events_dir = events_dir

        rc_service = MagicMock(spec=RoutechoicesService)
        rc_service.resolve_event_id.return_value = "rc_evt_1"
        # RC short_name is "aLiCe" — should match "Alice" case-insensitively
        rc_service.fetch_event_payload.return_value = RoutechoicesEventDataRaw(
            competitors=[
                RoutechoicesCompetitorRaw(id="c1", encoded_data=encoded, short_name="aLiCe"),
            ]
        )

        service = GpsPollingService(events=event_repo, logs=log_repo, rc=rc_service)
        await service.poll_once()

        log_file = events_dir / "evt1" / "logs" / "u1.json"
        assert log_file.exists()

    @pytest.mark.asyncio
    async def test_no_match_skips(self, tmp_path: Path) -> None:
        beacon = {"id": 31, "number": 1, "tag": "B1", "is_ph": False, "code": "AB", "coordinates": "46.0,6.0"}
        reg = {"user_id": "u1", "course_number": 1, "routechoices_short_name": "alice"}
        event_data = _make_event(
            beacons=[beacon],
            courses=[{"number": 1, "beacons": [31]}],
            registrations=[reg],
        )

        encoded = _encode_single_point(1000, 4600000, 600000)

        events_dir = tmp_path / "events"
        _setup_event(events_dir, event_data)

        event_repo = EventRepository()
        event_repo._events_dir = events_dir

        log_repo = LogRepository()
        log_repo._events_dir = events_dir

        rc_service = MagicMock(spec=RoutechoicesService)
        rc_service.resolve_event_id.return_value = "rc_evt_1"
        # Different short_name → no match
        rc_service.fetch_event_payload.return_value = RoutechoicesEventDataRaw(
            competitors=[
                RoutechoicesCompetitorRaw(id="c1", encoded_data=encoded, short_name="unknown"),
            ]
        )

        service = GpsPollingService(events=event_repo, logs=log_repo, rc=rc_service)
        await service.poll_once()

        log_file = events_dir / "evt1" / "logs" / "u1.json"
        assert not log_file.exists()


