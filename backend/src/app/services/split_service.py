from app.domain.competitor_state import CompetitorState
from app.domain.split_calculator import SplitCalculator
from app.repositories.event_repository import EventRepository
from app.repositories.log_repository import LogRepository
from app.repositories.user_repository import UserRepository
from app.schemas.splits import CompetitorSummary, SplitsResponse


class SplitService:
    """Orchestrates split time computation for an event."""

    def __init__(
        self,
        events: EventRepository | None = None,
        users: UserRepository | None = None,
        logs: LogRepository | None = None,
    ) -> None:
        self._events = events or EventRepository()
        self._users = users or UserRepository()
        self._logs = logs or LogRepository()
        self._calc = SplitCalculator()

    def compute(self, event_id: str) -> SplitsResponse:
        event = self._events.load(event_id)

        # Build competitor states and summaries
        states: dict[str, CompetitorState] = {}
        registrations_course: dict[str, int | None] = {}
        competitors: list[CompetitorSummary] = []

        for reg in event.registrations:
            user = self._users.find_by_id(reg.user_id)
            if not user:
                continue

            state = self._build_state(event_id, user.id)
            # Skip DNS competitors
            if state.dns:
                continue

            states[user.id] = state
            registrations_course[user.id] = reg.course_number
            competitors.append(CompetitorSummary(
                user_id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                sex=user.sex,
                course_number=reg.course_number,
            ))

        # Extract pairs and compute splits
        pairs = self._calc.extract_pairs(event)
        pair_splits = self._calc.compute_splits(pairs, states, registrations_course, event)

        return SplitsResponse(
            event_name=event.name,
            beacons=event.beacons,
            competitors=competitors,
            pairs=pair_splits,
        )

    def _build_state(self, event_id: str, user_id: str) -> CompetitorState:
        logs = self._logs.load(event_id, user_id)
        state = CompetitorState()
        for entry in logs:
            entry.apply_to(state)
        return state

