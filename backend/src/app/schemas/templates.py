from pydantic import BaseModel, Field


class Beacon(BaseModel):
    id: int = Field(ge=31)
    number: int
    tag: str
    is_ph: bool = False
    code: str | None = None
    coordinates: str | None = None


class Course(BaseModel):
    """Course as stored — beacons are referenced by id."""

    number: int
    beacons: list[int] = []


class CourseDetail(BaseModel):
    """Course as returned by GET — beacons are enriched with full info."""

    number: int
    beacons: list[Beacon] = []


class Gate(BaseModel):
    gate: str
    min_m: int | None = None
    max_m: int | None = None
    min_f: int | None = None
    max_f: int | None = None


class CourseTimeGates(BaseModel):
    course_number: int
    gates: list[Gate] = []


class NameBody(BaseModel):
    """Shared base for create/update operations that only require a name."""

    name: str = Field(min_length=1)


# Aliases for semantic clarity in routers
TemplateCreate = NameBody
TemplateUpdate = NameBody


class TemplateSummary(BaseModel):
    id: str
    name: str


class TemplateImportData(BaseModel):
    """Typed data for importing template content into an event."""

    beacons: list[Beacon] = []
    courses: list[Course] = []
    time_gates: list[CourseTimeGates] = []


