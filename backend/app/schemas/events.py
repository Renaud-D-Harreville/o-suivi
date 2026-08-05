from pydantic import BaseModel, Field

from app.schemas.templates import Beacon, Course, CourseDetail, CourseTimeGates, NameBody


class StartMode(BaseModel):
    group_size: int = 1
    interval_seconds: int = 120


class EventRegistration(BaseModel):
    user_id: str
    course_number: int | None = None
    start_order: int | None = None
    start_time_planned: str | None = None
    tracker_number: str | None = None


class EventBeacon(Beacon):
    """Beacon with an assigned 2-letter code for this event."""

    code: str = ""


# Reuse NameBody — same validation (name: str, min_length=1)
EventCreate = NameBody


class EventSummary(BaseModel):
    id: str
    name: str
    date: str | None = None


class EventDetail(BaseModel):
    id: str
    name: str
    date: str | None = None
    template_id: str | None = None
    first_start_time: str | None = None
    routechoices_url: str | None = None
    public_routechoices_time: str | None = None
    start_mode: StartMode | None = None
    beacons: list[EventBeacon] = []
    courses: list[CourseDetail] = []
    time_gates: list[CourseTimeGates] = []
    registrations: list[EventRegistration] = []


class ScheduleEntry(BaseModel):
    """One row of the public schedule view."""

    first_name: str
    last_name_initial: str
    phone: str | None = None
    start_time_planned: str | None = None


class ScheduleResponse(BaseModel):
    """Response for the public schedule endpoint."""

    event_name: str
    entries: list[ScheduleEntry]


class EventUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    date: str | None = None
    template_id: str | None = None
    first_start_time: str | None = None
    routechoices_url: str | None = None
    public_routechoices_time: str | None = None
    start_mode: StartMode | None = None
    beacons: list[EventBeacon] | None = None
    courses: list[Course] | None = None
    time_gates: list[CourseTimeGates] | None = None
    registrations: list[EventRegistration] | None = None
