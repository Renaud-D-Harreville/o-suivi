from pydantic import BaseModel

from app.domain.competitor_state import CheckpointEntry
from app.schemas.events import CourseDetail, CourseTimeGates, EventBeacon
from app.schemas.logs import LogEntry


class CompetitorTracking(BaseModel):
    """Full tracking state for one competitor."""

    user_id: str
    first_name: str
    last_name: str
    sex: str
    phone: str
    course_number: int | None = None
    start_order: int | None = None
    start_time_planned: str | None = None
    tracker_number: str | None = None
    departed: bool = False
    departure_time: str | None = None
    dns: bool = False
    abandoned: bool = False
    tracker_returned: bool = False
    bag_weight_start: float | None = None
    checkpoints: list[CheckpointEntry] = []
    ph_arrivals: dict[int, str] = {}
    logs: list[LogEntry] = []


class TrackingResponse(BaseModel):
    """Aggregated tracking data for an event (serves Départ + Suivi views)."""

    name: str
    courses: list[CourseDetail] = []
    time_gates: list[CourseTimeGates] = []
    beacons: list[EventBeacon] = []
    competitors: list[CompetitorTracking] = []

