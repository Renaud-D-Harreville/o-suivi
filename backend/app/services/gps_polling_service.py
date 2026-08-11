"""GPS polling service — fetches Routechoices data and detects beacon passages."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from app.domain.competitor_state import CompetitorState
from app.domain.geo_utils import haversine_distance, parse_coordinates
from app.domain.gps_decoder import GpsPoint, decode_position_archive
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

        # Sort by timestamp ascending
        points.sort(key=lambda p: p.timestamp_ms)

        # Reconstruct current state
        raw_logs = self._logs.load_raw(event.id, reg.user_id)
        state = CompetitorState.from_logs(raw_logs)

        # Get course beacons
        course_beacons = self._events.get_course_beacons(event, reg.course_number)
        if not course_beacons:
            return

        wrote_any = False
        for idx, beacon in enumerate(course_beacons):
            seq = idx + 1
            wrote = await self._check_beacon(event.id, reg.user_id, state, beacon, seq, points)
            if wrote:
                logger.info(
                    "GPS poll: wrote log for user %s, beacon seq=%d (%s)",
                    reg.user_id, seq, beacon.tag,
                )
                wrote_any = True

        if wrote_any:
            await manager.broadcast_refresh(event.id)

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
        # Already has a passage_time → skip
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
            event_id, user_id, beacon, sequence, points, b_lat, b_lon
        )

    async def _check_normal_beacon(
        self,
        event_id: str,
        user_id: str,
        beacon: EventBeacon,
        sequence: int,
        points: list[GpsPoint],
        b_lat: float,
        b_lon: float,
    ) -> bool:
        """Normal beacon: write checkpoint_edit at first point ≤ 25m."""
        for point in points:
            dist = haversine_distance(point.lat, point.lon, b_lat, b_lon)
            if dist <= _DETECTION_RADIUS_M:
                passage_time = _timestamp_to_iso(point.timestamp_ms)
                entry = CheckpointEditLog(
                    metadata=_gps_metadata(passage_time),
                    data=CheckpointEditData(
                        sequence=sequence,
                        code=beacon.code or None,
                        passage_time=passage_time,
                    ),
                )
                self._logs.append(event_id, user_id, entry)
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
        """PH beacon: ph_arrival_edit on entry, checkpoint_edit on exit."""
        has_arrival = sequence in state.ph_arrivals

        if not has_arrival:
            # Look for entry: first point ≤ 25m
            for point in points:
                dist = haversine_distance(point.lat, point.lon, b_lat, b_lon)
                if dist <= _DETECTION_RADIUS_M:
                    passage_time = _timestamp_to_iso(point.timestamp_ms)
                    entry = PhArrivalEditLog(
                        metadata=_gps_metadata(passage_time),
                        data=PhArrivalEditData(
                            sequence=sequence,
                            passage_time=passage_time,
                        ),
                    )
                    self._logs.append(event_id, user_id, entry)
                    return True
            return False

        # Has arrival but no checkpoint → look for exit: first point > 25m after entry
        # Find the entry timestamp from ph_arrivals to only look at points after entry
        entry_time_hms = state.ph_arrivals[sequence]
        entered = False
        for point in points:
            dist = haversine_distance(point.lat, point.lon, b_lat, b_lon)
            if not entered:
                if dist <= _DETECTION_RADIUS_M:
                    entered = True
                continue
            # After entering, look for exit
            if dist > _DETECTION_RADIUS_M:
                passage_time = _timestamp_to_iso(point.timestamp_ms)
                entry = CheckpointEditLog(
                    metadata=_gps_metadata(passage_time),
                    data=CheckpointEditData(
                        sequence=sequence,
                        code=beacon.code or None,
                        passage_time=passage_time,
                    ),
                )
                self._logs.append(event_id, user_id, entry)
                return True
        return False


def _gps_metadata(creation_date: str) -> LogMetadata:
    """Build log metadata for a GPS-originated entry."""
    return LogMetadata(
        creation_date=creation_date,
        received_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        author_id="gps",
    )


def _timestamp_to_iso(timestamp_ms: int) -> str:
    """Convert a Unix timestamp in milliseconds to ISO 8601 string."""
    return datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc).isoformat(timespec="seconds")





