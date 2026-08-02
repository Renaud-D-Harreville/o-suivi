from pydantic import BaseModel

from app.domain.competitor_state import CheckpointEntry, CompetitorState
from app.repositories.log_repository import LogRepository


class CheckpointResponse(BaseModel):
    """Response containing checkpoints and PH arrival times."""

    checkpoints: list[CheckpointEntry]
    ph_arrivals: dict[int, str]  # sequence -> arrival timestamp


class CheckpointService:
    """Returns the current checkpoint state for a competitor."""

    def __init__(self, logs: LogRepository | None = None) -> None:
        self._logs = logs or LogRepository()

    def get_checkpoints(self, event_id: str, user_id: str) -> list[CheckpointEntry]:
        state = self._build_state(event_id, user_id)
        return list(state.checkpoints.values())

    def get_checkpoints_with_arrivals(self, event_id: str, user_id: str) -> CheckpointResponse:
        state = self._build_state(event_id, user_id)
        return CheckpointResponse(
            checkpoints=list(state.checkpoints.values()),
            ph_arrivals=dict(state.ph_arrivals),
        )

    def _build_state(self, event_id: str, user_id: str) -> CompetitorState:
        logs = self._logs.load(event_id, user_id)
        state = CompetitorState()
        for entry in logs:
            entry.apply_to(state)
        return state

