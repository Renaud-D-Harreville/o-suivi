import uuid

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import require_organizer
from app.repositories.event_repository import EventRepository
from app.repositories.template_repository import TemplateRepository
from app.schemas.events import EventCreate, EventDetail, EventSummary, EventUpdate
from app.schemas.routechoices import RoutechoicesGpsRawResponse
from app.schemas.tracking import TrackingResponse
from app.services.routechoices_service import (
    RoutechoicesResolutionError,
    RoutechoicesService,
    RoutechoicesUpstreamError,
)
from app.services.tracking_service import TrackingService

router = APIRouter(
    prefix="/api/events",
    tags=["events"],
)

_auth = [Depends(require_organizer)]


def _events() -> EventRepository:
    return EventRepository()


@router.get("", response_model=list[EventSummary])
async def list_events() -> list[EventSummary]:
    return _events().list_all()


@router.post("", response_model=EventSummary, status_code=201, dependencies=_auth)
async def create_event(body: EventCreate) -> EventSummary:
    return _events().create(str(uuid.uuid4()), body.name)


@router.get("/{event_id}", response_model=EventDetail, dependencies=_auth)
async def get_event(event_id: str) -> EventDetail:
    return _events().load(event_id)


@router.patch("/{event_id}", response_model=EventDetail, dependencies=_auth)
async def update_event(event_id: str, body: EventUpdate) -> EventDetail:
    return _events().update(event_id, body)


@router.post("/{event_id}/import-template", response_model=EventDetail, dependencies=_auth)
async def import_template(event_id: str) -> EventDetail:
    event = _events().load(event_id)
    if not event.template_id:
        raise HTTPException(status_code=400, detail="No template selected for this event")
    template_data = TemplateRepository().get_import_data(event.template_id)
    return _events().import_template(event_id, template_data)


@router.get("/{event_id}/tracking", response_model=TrackingResponse, dependencies=_auth)
async def get_tracking(event_id: str) -> TrackingResponse:
    return TrackingService().get_tracking(event_id)


@router.get("/{event_id}/routechoices/gps", response_model=RoutechoicesGpsRawResponse, dependencies=_auth)
async def get_routechoices_gps(event_id: str) -> RoutechoicesGpsRawResponse:
    event_repo = _events()
    event = event_repo.load(event_id)
    service = RoutechoicesService()

    try:
        routechoices_event_id = service.resolve_event_id(event)
        payload = service.fetch_event_payload(routechoices_event_id)
    except RoutechoicesResolutionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RoutechoicesUpstreamError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    if not event.routechoices_event_id:
        event_repo.set_routechoices_event_id(event_id, routechoices_event_id)

    return RoutechoicesGpsRawResponse(routechoices_event_id=routechoices_event_id, payload=payload)


