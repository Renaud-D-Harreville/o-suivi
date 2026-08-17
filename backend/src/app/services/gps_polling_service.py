"""GPS polling service — fetches Routechoices data and detects beacon passages."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from app.domain.competitor_state import CompetitorState
from app.domain.geo_utils import haversine_distance, parse_coordinates
from app.domain.gps_decoder import GpsPoint, decode_position_archive
from app.domain.time_utils import to_hms
from app.repositories.event_repository import EventRepository
from app.repositories.log_repository import LogRepository
from app.schemas.events import EventBeacon, EventDetail, EventRegistration
from app.schemas.logs import (
    CheckpointEditData,
    CheckpointEditLog,
    LogMetadata,
    PhArrivalEditData,
    PhArrivalEditLog,
)
from app.schemas.routechoices import RoutechoicesCompetitorRaw
from app.services.routechoices_service import (
    RoutechoicesResolutionError,
    RoutechoicesService,
    RoutechoicesUpstreamError,
)
from app.websocket.connection_manager import manager

logger = logging.getLogger(__name__)

_DETECTION_RADIUS_M = 25.0


_PARIS_TZ = ZoneInfo("Europe/Paris")


class GpsPollingService:
    """Fetches Routechoices GPS data and writes beacon-passage logs."""

    def __init__(
        self,
        events: EventRepository | None = None,
        logs: LogRepository | None = None,
        rc: RoutechoicesService | None = None,
    ) -> None:
        self._events = events or EventRepository()
        self._logs = logs or LogRepository()
        self._rc = rc or RoutechoicesService()

    async def poll_once(self) -> None:
        """Run a single polling cycle for all events with GPS polling enabled."""
        events = self._events.list_all()
        for summary in events:
            try:
                event = self._events.load(summary.id)
            except Exception:
                logger.exception("Failed to load event %s", summary.id)
                continue

            if not event.gps_polling_enabled:
                continue

            logger.info("GPS poll: processing event '%s' (%s)", event.name, event.id)
            await self._poll_event(event)

    async def _poll_event(self, event: EventDetail) -> None:
        """Poll a single event: fetch RC data, match competitors, detect beacons."""
        try:
            rc_event_id = self._rc.resolve_event_id(event)
            rc_data = self._rc.fetch_event_payload(rc_event_id)
        except (RoutechoicesResolutionError, RoutechoicesUpstreamError) as exc:
            logger.warning("GPS poll skipped for event %s: %s", event.id, exc)
            return

        logger.info(
            "GPS poll: fetched %d RC competitors for event %s",
            len(rc_data.competitors), event.id,
        )

        # Build short_name → registration mapping (case-insensitive)
        sn_to_reg: dict[str, EventRegistration] = {}
        for reg in event.registrations:
            if reg.routechoices_short_name:
                sn_to_reg[reg.routechoices_short_name.lower()] = reg

        if not sn_to_reg:
            logger.warning(
                "GPS poll: no registrations with routechoices_short_name for event %s",
                event.id,
            )
            return

        matched = 0
        for rc_competitor in rc_data.competitors:
            if not rc_competitor.short_name:
                continue
            reg = sn_to_reg.get(rc_competitor.short_name.lower())
            if reg is None:
                logger.debug(
                    "GPS poll: RC competitor '%s' has no matching registration",
                    rc_competitor.short_name,
                )
                continue

            matched += 1
            await self._process_competitor(event, reg, rc_competitor)

        logger.info("GPS poll: matched %d/%d competitors for event %s", matched, len(rc_data.competitors), event.id)

    async def _process_competitor(
        self,
        event: EventDetail,
        reg: EventRegistration,
        rc_competitor: RoutechoicesCompetitorRaw,
    ) -> None:
        """Decode GPS data and detect beacon passages for one competitor."""
        points = decode_position_archive(rc_competitor.encoded_data)
        if not points:
            return

        points.sort(key=lambda p: p.timestamp_ms)

        raw_logs = self._logs.load_raw(event.id, reg.user_id)
        state = CompetitorState.from_logs(raw_logs)

        if not state.departed or not state.departure_time:
            return

        departure_dt = self._parse_departure_time(event, state.departure_time)
        if departure_dt:
            departure_ms = int(departure_dt.timestamp() * 1000)
            points = [p for p in points if p.timestamp_ms >= departure_ms]
            if not points:
                return

        course_beacons = self._events.get_course_beacons(event, reg.course_number)
        if not course_beacons:
            return

        wrote_any = await self._detect_beacons(event.id, reg.user_id, state, course_beacons, points)

        cleaned = await self._cleanup_inconsistencies(event.id, reg.user_id, state, course_beacons)

        if wrote_any or cleaned:
            await manager.broadcast_refresh(event.id)

    def _parse_departure_time(self, event: EventDetail, departure_time: str) -> datetime | None:
        """Convert a departure_time (HH:MM:SS) to a timezone-aware datetime using the event date."""
        try:
            time_parts = departure_time.split(":")
            h, m = int(time_parts[0]), int(time_parts[1])
            s = int(time_parts[2]) if len(time_parts) > 2 else 0
            event_date = event.date if event.date else None
            if event_date:
                year, month, day = (int(x) for x in event_date.split("-"))
                return datetime(year, month, day, h, m, s, tzinfo=_PARIS_TZ)
            return None
        except (ValueError, IndexError, AttributeError):
            return None

    # --- Detection (with chronological guard) ---

    async def _detect_beacons(
        self,
        event_id: str,
        user_id: str,
        state: CompetitorState,
        course_beacons: list[EventBeacon],
        points: list[GpsPoint],
    ) -> bool:
        """Detect beacon passages with chronological guard. Returns True if any log was written."""
        wrote_any = False
        for idx, beacon in enumerate(course_beacons):
            seq = idx + 1
            wrote = await self._check_beacon(event_id, user_id, state, beacon, seq, points)
            if wrote:
                logger.info(
                    "GPS poll: wrote log for user %s, beacon seq=%d (%s)",
                    user_id, seq, beacon.tag,
                )
                wrote_any = True
        return wrote_any

    async def _check_beacon(
        self,
        event_id: str,
        user_id: str,
        state: CompetitorState,
        beacon: EventBeacon,
        sequence: int,
        points: list[GpsPoint],
    ) -> bool:
        """Check a single beacon for GPS proximity. Returns True if a log was written."""
        cp = state.checkpoints.get(sequence)
        if cp and cp.passage_time:
            return False

        beacon_coords = parse_coordinates(beacon.coordinates or "")
        if beacon_coords is None:
            return False
        b_lat, b_lon = beacon_coords

        if beacon.is_ph:
            return await self._check_ph_beacon(
                event_id, user_id, state, beacon, sequence, points, b_lat, b_lon
            )
        return await self._check_normal_beacon(
            event_id, user_id, state, beacon, sequence, points, b_lat, b_lon
        )

    def _max_previous_passage_time(self, state: CompetitorState, sequence: int) -> str | None:
        """Return the latest passage_time among all checkpoints with seq < sequence."""
        max_time: str | None = None
        for seq, cp in state.checkpoints.items():
            if seq < sequence and cp.passage_time:
                if max_time is None or cp.passage_time > max_time:
                    max_time = cp.passage_time
        return max_time

    def _is_chronologically_valid(self, passage_time_hms: str, state: CompetitorState, sequence: int) -> bool:
        """Return True if passage_time is strictly after all previous checkpoints."""
        max_prev = self._max_previous_passage_time(state, sequence)
        if max_prev is None:
            return True
        return passage_time_hms > max_prev

    async def _check_normal_beacon(
        self,
        event_id: str,
        user_id: str,
        state: CompetitorState,
        beacon: EventBeacon,
        sequence: int,
        points: list[GpsPoint],
        b_lat: float,
        b_lon: float,
    ) -> bool:
        """Normal beacon: write checkpoint_edit at first point ≤ 25m (with chronological guard)."""
        for point in points:
            dist = haversine_distance(point.lat, point.lon, b_lat, b_lon)
            if dist <= _DETECTION_RADIUS_M:
                passage_time = _timestamp_to_iso(point.timestamp_ms)
                passage_hms = to_hms(passage_time)
                if not passage_hms or not self._is_chronologically_valid(passage_hms, state, sequence):
                    return False
                entry = CheckpointEditLog(
                    metadata=_gps_metadata(passage_time),
                    data=CheckpointEditData(
                        sequence=sequence,
                        code=beacon.code or None,
                        passage_time=passage_time,
                    ),
                )
                self._logs.append(event_id, user_id, entry)
                entry.apply_to(state)
                return True
        return False

    async def _check_ph_beacon(
        self,
        event_id: str,
        user_id: str,
        state: CompetitorState,
        beacon: EventBeacon,
        sequence: int,
        points: list[GpsPoint],
        b_lat: float,
        b_lon: float,
    ) -> bool:
        """PH beacon: ph_arrival_edit on entry (with guard), checkpoint_edit on exit (with guard)."""
        has_arrival = sequence in state.ph_arrivals

        if not has_arrival:
            return await self._detect_ph_entry(
                event_id, user_id, state, sequence, points, b_lat, b_lon
            )
        return await self._detect_ph_exit(
            event_id, user_id, state, beacon, sequence, points, b_lat, b_lon
        )

    async def _detect_ph_entry(
        self,
        event_id: str,
        user_id: str,
        state: CompetitorState,
        sequence: int,
        points: list[GpsPoint],
        b_lat: float,
        b_lon: float,
    ) -> bool:
        """Detect PH entry: first point ≤ 25m, with chronological guard."""
        for point in points:
            dist = haversine_distance(point.lat, point.lon, b_lat, b_lon)
            if dist <= _DETECTION_RADIUS_M:
                passage_time = _timestamp_to_iso(point.timestamp_ms)
                passage_hms = to_hms(passage_time)
                if not passage_hms or not self._is_chronologically_valid(passage_hms, state, sequence):
                    return False
                entry = PhArrivalEditLog(
                    metadata=_gps_metadata(passage_time),
                    data=PhArrivalEditData(
                        sequence=sequence,
                        passage_time=passage_time,
                    ),
                )
                self._logs.append(event_id, user_id, entry)
                entry.apply_to(state)
                return True
        return False

    async def _detect_ph_exit(
        self,
        event_id: str,
        user_id: str,
        state: CompetitorState,
        beacon: EventBeacon,
        sequence: int,
        points: list[GpsPoint],
        b_lat: float,
        b_lon: float,
    ) -> bool:
        """Detect PH exit: first point > 25m after entry, with chronological guard."""
        entered = False
        for point in points:
            dist = haversine_distance(point.lat, point.lon, b_lat, b_lon)
            if not entered:
                if dist <= _DETECTION_RADIUS_M:
                    entered = True
                continue
            if dist > _DETECTION_RADIUS_M:
                passage_time = _timestamp_to_iso(point.timestamp_ms)
                passage_hms = to_hms(passage_time)
                if not passage_hms or not self._is_chronologically_valid(passage_hms, state, sequence):
                    return False
                entry = CheckpointEditLog(
                    metadata=_gps_metadata(passage_time),
                    data=CheckpointEditData(
                        sequence=sequence,
                        code=beacon.code or None,
                        passage_time=passage_time,
                    ),
                )
                self._logs.append(event_id, user_id, entry)
                entry.apply_to(state)
                return True
        return False


    # --- Cleanup: remove GPS-written checkpoints that break chronological order ---

    async def _cleanup_inconsistencies(
        self,
        event_id: str,
        user_id: str,
        state: CompetitorState,
        course_beacons: list[EventBeacon],
    ) -> bool:
        """Remove GPS-authored checkpoints whose passage_time breaks chronological order."""
        to_clear = self._find_inconsistent_gps_checkpoints(state, len(course_beacons))
        for seq in to_clear:
            self._write_clear_log(event_id, user_id, seq)
            logger.info("GPS poll: cleaned inconsistent beacon seq=%d for user %s", seq, user_id)
        return len(to_clear) > 0

    def _find_inconsistent_gps_checkpoints(
        self, state: CompetitorState, beacon_count: int,
    ) -> list[int]:
        """Return sequences of GPS-authored checkpoints that are out of chronological order."""
        inconsistent: list[int] = []
        for seq in range(1, beacon_count + 1):
            cp = state.checkpoints.get(seq)
            if not cp or not cp.passage_time:
                continue
            if cp.author_id != "gps":
                continue
            max_prev = self._max_previous_passage_time(state, seq)
            if max_prev is not None and cp.passage_time < max_prev:
                inconsistent.append(seq)
        return inconsistent

    def _write_clear_log(self, event_id: str, user_id: str, sequence: int) -> None:
        """Write a checkpoint_edit with null passage_time and code to clear a false detection."""
        entry = CheckpointEditLog(
            metadata=_gps_metadata(
                datetime.now(_PARIS_TZ).isoformat(timespec="seconds"),
            ),
            data=CheckpointEditData(
                sequence=sequence,
                code=None,
                passage_time=None,
            ),
        )
        self._logs.append(event_id, user_id, entry)


def _gps_metadata(creation_date: str) -> LogMetadata:
    """Build log metadata for a GPS-originated entry."""
    return LogMetadata(
        creation_date=creation_date,
        received_at=datetime.now(_PARIS_TZ).isoformat(timespec="seconds"),
        author_id="gps",
    )


def _timestamp_to_iso(timestamp_ms: int) -> str:
    """Convert a Unix timestamp in milliseconds to ISO 8601 string in Europe/Paris timezone."""
    return datetime.fromtimestamp(timestamp_ms / 1000, tz=_PARIS_TZ).isoformat(timespec="seconds")





