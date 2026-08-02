import uuid

from fastapi import APIRouter, Depends

from app.dependencies import require_organizer
from app.repositories.template_repository import TemplateRepository
from app.schemas.templates import (
    Beacon,
    Course,
    CourseDetail,
    CourseTimeGates,
    TemplateCreate,
    TemplateSummary,
    TemplateUpdate,
)

router = APIRouter(
    prefix="/api/templates",
    tags=["templates"],
    dependencies=[Depends(require_organizer)],
)


def _repo() -> TemplateRepository:
    return TemplateRepository()


# --- Template CRUD -----------------------------------------------------------


@router.get("", response_model=list[TemplateSummary])
async def list_templates() -> list[TemplateSummary]:
    return _repo().list_all()


@router.post("", response_model=TemplateSummary, status_code=201)
async def create_template(body: TemplateCreate) -> TemplateSummary:
    return _repo().create(str(uuid.uuid4()), body.name)


@router.get("/{template_id}", response_model=TemplateSummary)
async def get_template(template_id: str) -> TemplateSummary:
    return _repo().load(template_id)


@router.patch("/{template_id}", response_model=TemplateSummary)
async def update_template(template_id: str, body: TemplateUpdate) -> TemplateSummary:
    return _repo().update_name(template_id, body.name)


# --- Beacons section ----------------------------------------------------------


@router.get("/{template_id}/beacons", response_model=list[Beacon])
async def get_beacons(template_id: str) -> list[Beacon]:
    return _repo().get_beacons(template_id)


@router.put("/{template_id}/beacons", response_model=list[Beacon])
async def replace_beacons(template_id: str, body: list[Beacon]) -> list[Beacon]:
    return _repo().replace_beacons(template_id, body)


# --- Courses section ----------------------------------------------------------


@router.get("/{template_id}/courses", response_model=list[CourseDetail])
async def get_courses(template_id: str) -> list[CourseDetail]:
    return _repo().get_courses(template_id)


@router.put("/{template_id}/courses", response_model=list[CourseDetail])
async def replace_courses(template_id: str, body: list[Course]) -> list[CourseDetail]:
    return _repo().replace_courses(template_id, body)


# --- Time gates section -------------------------------------------------------


@router.get("/{template_id}/time-gates", response_model=list[CourseTimeGates])
async def get_time_gates(template_id: str) -> list[CourseTimeGates]:
    return _repo().get_time_gates(template_id)


@router.put("/{template_id}/time-gates", response_model=list[CourseTimeGates])
async def replace_time_gates(
    template_id: str, body: list[CourseTimeGates]
) -> list[CourseTimeGates]:
    return _repo().replace_time_gates(template_id, body)
