from pydantic import BaseModel, Field, TypeAdapter

from app.schemas.logs import LogEntry

_LOG_LIST_ADAPTER = TypeAdapter(list[LogEntry])


class CheckpointEntry(BaseModel):
    """A validated checkpoint passage (sequence + code + passage time)."""

    sequence: int
    code: str | None = None
    passage_time: str | None = None


class CompetitorState(BaseModel):
    """Reconstructed state of a competitor from their log entries."""

    departed: bool = False
    departure_time: str | None = None
    dns: bool = False
    abandoned: bool = False
    tracker_returned: bool = False
    bag_weight_start: float | None = None
    bag_weight_end: float | None = None
    checkpoints: dict[int, CheckpointEntry] = Field(default_factory=dict)
    ph_arrivals: dict[int, str] = Field(default_factory=dict)
    skipped: set[int] = Field(default_factory=set)

    @classmethod
    def from_logs(cls, raw_logs: list[dict]) -> "CompetitorState":
        """Parse raw log dicts and apply each entry polymorphically."""
        entries = _LOG_LIST_ADAPTER.validate_python(raw_logs)
        state = cls()
        for entry in entries:
            entry.apply_to(state)
        return state
