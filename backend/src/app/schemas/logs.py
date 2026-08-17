from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Literal

from pydantic import BaseModel, Field

from app.domain.time_utils import to_hms

if TYPE_CHECKING:
    from app.domain.competitor_state import CompetitorState


# --- Metadata (common to ALL log entries) ---


class LogMetadata(BaseModel):
    """Contextual info attached to every log entry."""

    creation_date: str  # when the action happened (client clock)
    received_at: str  # when the server received it
    author_id: str  # who performed the action
    author_name: str = ""  # resolved at read time, not stored


# --- Data classes for log entries with payload ---


class CommentData(BaseModel):
    """Shared data for log entries that carry a comment."""

    comment: str = Field(min_length=1)



class DepartureData(BaseModel):
    departure_time: str = Field(min_length=1)


class BagWeightData(BaseModel):
    moment: Literal["start", "end"]
    weight_kg: float = Field(gt=0)


class TrackerReturnedData(BaseModel):
    tracker_number: str = Field(min_length=1)


class DepartureEditData(BaseModel):
    departure_time: str = Field(min_length=1)


class CheckpointData(BaseModel):
    sequence: int = Field(ge=1)
    code: str = Field(min_length=2, max_length=2)
    passage_time: str | None = None


class CheckpointEditData(BaseModel):
    sequence: int = Field(ge=1)
    code: str | None = Field(default=None, min_length=2, max_length=2)
    passage_time: str | None = None
    comment: str | None = None


class PhArrivalData(BaseModel):
    sequence: int = Field(ge=1)
    passage_time: str | None = None


class PhArrivalEditData(BaseModel):
    sequence: int = Field(ge=1)
    passage_time: str = Field(min_length=1)


class SkipData(BaseModel):
    checkpoint: int = Field(ge=1)


SkipCancelData = SkipData


# --- Log entries (stored in JSON files) ---


class BaseLogEntry(BaseModel):
    """Base for ALL log types. Subclasses add `data` if they carry a payload."""

    metadata: LogMetadata

    def apply_to(self, state: CompetitorState) -> None:
        """Apply this entry to a competitor state. No-op by default."""


class DepartureLog(BaseLogEntry):
    log_type: Literal["departure"] = "departure"
    data: DepartureData | None = None

    def apply_to(self, state: CompetitorState) -> None:
        state.departed = True
        state.departure_time = to_hms(self.data.departure_time) if self.data else None


class DepartureCancelLog(BaseLogEntry):
    log_type: Literal["departure_cancel"] = "departure_cancel"

    def apply_to(self, state: CompetitorState) -> None:
        state.departed = False
        state.departure_time = None


class DepartureEditLog(BaseLogEntry):
    log_type: Literal["departure_edit"] = "departure_edit"
    data: DepartureEditData

    def apply_to(self, state: CompetitorState) -> None:
        state.departed = True
        state.departure_time = to_hms(self.data.departure_time)


class DnsLog(BaseLogEntry):
    log_type: Literal["dns"] = "dns"
    data: CommentData

    def apply_to(self, state: CompetitorState) -> None:
        state.dns = True


class DnsCancelLog(BaseLogEntry):
    log_type: Literal["dns_cancel"] = "dns_cancel"
    data: CommentData

    def apply_to(self, state: CompetitorState) -> None:
        state.dns = False


class BagWeightLog(BaseLogEntry):
    log_type: Literal["bag_weight"] = "bag_weight"
    data: BagWeightData

    def apply_to(self, state: CompetitorState) -> None:
        if self.data.moment == "start":
            state.bag_weight_start = self.data.weight_kg
        else:
            state.bag_weight_end = self.data.weight_kg


class AbandonLog(BaseLogEntry):
    log_type: Literal["abandon"] = "abandon"
    data: CommentData

    def apply_to(self, state: CompetitorState) -> None:
        state.abandoned = True


class AbandonCancelLog(BaseLogEntry):
    log_type: Literal["abandon_cancel"] = "abandon_cancel"
    data: CommentData

    def apply_to(self, state: CompetitorState) -> None:
        state.abandoned = False


class TrackerReturnedLog(BaseLogEntry):
    log_type: Literal["tracker_returned"] = "tracker_returned"
    data: TrackerReturnedData

    def apply_to(self, state: CompetitorState) -> None:
        state.tracker_returned = True


class TrackerReturnedCancelLog(BaseLogEntry):
    log_type: Literal["tracker_returned_cancel"] = "tracker_returned_cancel"

    def apply_to(self, state: CompetitorState) -> None:
        state.tracker_returned = False


class CheckpointLog(BaseLogEntry):
    log_type: Literal["checkpoint"] = "checkpoint"
    data: CheckpointData

    def apply_to(self, state: CompetitorState) -> None:
        from app.domain.competitor_state import CheckpointEntry

        state.checkpoints[self.data.sequence] = CheckpointEntry(
            sequence=self.data.sequence,
            code=self.data.code,
            passage_time=to_hms(self.data.passage_time),
            author_id=self.metadata.author_id,
        )


class CheckpointEditLog(BaseLogEntry):
    log_type: Literal["checkpoint_edit"] = "checkpoint_edit"
    data: CheckpointEditData

    def apply_to(self, state: CompetitorState) -> None:
        from app.domain.competitor_state import CheckpointEntry

        state.checkpoints[self.data.sequence] = CheckpointEntry(
            sequence=self.data.sequence,
            code=self.data.code,
            passage_time=to_hms(self.data.passage_time),
            author_id=self.metadata.author_id,
        )


class PhArrivalLog(BaseLogEntry):
    log_type: Literal["ph_arrival"] = "ph_arrival"
    data: PhArrivalData

    def apply_to(self, state: CompetitorState) -> None:
        state.ph_arrivals[self.data.sequence] = to_hms(self.data.passage_time)


class PhArrivalEditLog(BaseLogEntry):
    log_type: Literal["ph_arrival_edit"] = "ph_arrival_edit"
    data: PhArrivalEditData

    def apply_to(self, state: CompetitorState) -> None:
        state.ph_arrivals[self.data.sequence] = to_hms(self.data.passage_time)


class SkipLog(BaseLogEntry):
    log_type: Literal["skip"] = "skip"
    data: SkipData

    def apply_to(self, state: CompetitorState) -> None:
        state.skipped.add(self.data.checkpoint)


class SkipCancelLog(BaseLogEntry):
    log_type: Literal["skip_cancel"] = "skip_cancel"
    data: SkipCancelData

    def apply_to(self, state: CompetitorState) -> None:
        state.skipped.discard(self.data.checkpoint)


# Discriminated union for reading logs
LogEntry = Annotated[
    DepartureLog
    | DepartureCancelLog
    | DepartureEditLog
    | DnsLog
    | DnsCancelLog
    | BagWeightLog
    | AbandonLog
    | AbandonCancelLog
    | TrackerReturnedLog
    | TrackerReturnedCancelLog
    | CheckpointLog
    | CheckpointEditLog
    | PhArrivalLog
    | PhArrivalEditLog
    | SkipLog
    | SkipCancelLog,
    Field(discriminator="log_type"),
]


# --- Request schemas (what the client sends) ---


class BaseRequest(BaseModel):
    """Base for all requests — carries the client's action time."""

    creation_date: str


class DepartureRequest(BaseRequest):
    departure_time: str = Field(min_length=1)

DepartureCancelRequest = BaseRequest
TrackerReturnedCancelRequest = BaseRequest


class DepartureEditRequest(BaseRequest):
    """Request to correct the departure time."""

    departure_time: str = Field(min_length=1)


class CommentRequest(BaseRequest):
    """Request with creation_date + mandatory comment."""

    comment: str = Field(min_length=1)


DnsRequest = CommentRequest
DnsCancelRequest = CommentRequest
AbandonRequest = CommentRequest
AbandonCancelRequest = CommentRequest


class BagWeightRequest(BaseRequest):
    moment: Literal["start", "end"]
    weight_kg: float = Field(gt=0)


class TrackerReturnedRequest(BaseRequest):
    tracker_number: str = Field(min_length=1)


class CheckpointEditRequest(BaseRequest):
    """Edit a checkpoint — passage_time is the corrected time (optional)."""

    passage_time: str | None = None
    sequence: int = Field(ge=1)
    code: str | None = Field(default=None, min_length=2, max_length=2)
    comment: str | None = None


class PhArrivalEditRequest(BaseRequest):
    """Edit the arrival time at a PH gate."""

    sequence: int = Field(ge=1)
    passage_time: str = Field(min_length=1)

