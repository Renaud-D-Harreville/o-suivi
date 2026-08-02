from app.domain.competitor_state import CompetitorState
from app.repositories.event_repository import EventRepository
from app.repositories.log_repository import LogRepository
from app.repositories.user_repository import UserRepository
from app.schemas.events import EventRegistration
from app.schemas.logs import LogEntry
from app.schemas.tracking import CompetitorTracking, TrackingResponse


class TrackingService:
    """Aggregates all tracking data for an event in a single call."""

    def __init__(
        self,
        events: EventRepository | None = None,
        users: UserRepository | None = None,
        logs: LogRepository | None = None,
    ) -> None:
        self._events = events or EventRepository()
        self._users = users or UserRepository()
        self._logs = logs or LogRepository()

    def get_tracking(self, event_id: str) -> TrackingResponse:
        event = self._events.load(event_id)
        competitors = [
            self._build_competitor(event_id, reg)
            for reg in event.registrations
            if self._users.find_by_id(reg.user_id)
        ]

        return TrackingResponse(
            name=event.name,
            courses=event.courses,
            time_gates=event.time_gates,
            beacons=event.beacons,
            competitors=competitors,
        )

    def _build_competitor(self, event_id: str, reg: EventRegistration) -> CompetitorTracking:
        user = self._users.find_by_id(reg.user_id)
        assert user is not None

        logs = self._logs.load(event_id, user.id)
        state = CompetitorState()
        for entry in logs:
            entry.apply_to(state)

        enriched_logs = self._enrich_author_names(logs)

        return CompetitorTracking(
            user_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            sex=user.sex or "",
            phone=user.phone or "",
            course_number=reg.course_number,
            start_order=reg.start_order,
            start_time_planned=reg.start_time_planned,
            tracker_number=reg.tracker_number,
            departed=state.departed,
            departure_time=state.departure_time,
            dns=state.dns,
            abandoned=state.abandoned,
            tracker_returned=state.tracker_returned,
            bag_weight_start=state.bag_weight_start,
            checkpoints=list(state.checkpoints.values()),
            ph_arrivals=dict(state.ph_arrivals),
            logs=enriched_logs,
        )

    def _enrich_author_names(self, logs: list[LogEntry]) -> list[LogEntry]:
        """Return log entries with author_name resolved (no mutation of originals)."""
        cache: dict[str, str] = {}
        enriched: list[LogEntry] = []
        for entry in logs:
            author_id = entry.metadata.author_id
            if author_id not in cache:
                if author_id == "public":
                    cache[author_id] = "public"
                else:
                    author = self._users.find_by_id(author_id)
                    cache[author_id] = (
                        author.first_name or author.username or "?"
                    ) if author else "?"
            new_metadata = entry.metadata.model_copy(update={"author_name": cache[author_id]})
            enriched.append(entry.model_copy(update={"metadata": new_metadata}))
        return enriched
