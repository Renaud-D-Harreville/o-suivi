from fastapi import APIRouter, Depends

from app.dependencies import require_organizer
from app.domain.competitor_state import CheckpointEntry
from app.schemas.registrations import (
    RegistrationCreate,
    RegistrationDetail,
    RegistrationUpdate,
)
from app.services.checkpoint_service import CheckpointService
from app.services.registration_service import RegistrationService
from app.websocket.connection_manager import manager

router = APIRouter(
    prefix="/api/events/{event_id}/registrations",
    tags=["registrations"],
    dependencies=[Depends(require_organizer)],
)


def _service() -> RegistrationService:
    return RegistrationService()


@router.get("", response_model=list[RegistrationDetail])
async def list_registrations(event_id: str) -> list[RegistrationDetail]:
    return _service().list_all(event_id)


@router.get("/{user_id}/checkpoints", response_model=list[CheckpointEntry])
async def get_checkpoints(event_id: str, user_id: str) -> list[CheckpointEntry]:
    return CheckpointService().get_checkpoints(event_id, user_id)


@router.post("", response_model=RegistrationDetail, status_code=201)
async def add_registration(event_id: str, body: RegistrationCreate) -> RegistrationDetail:
    return _service().add(event_id, body)


@router.delete("/{user_id}", status_code=204)
async def remove_registration(event_id: str, user_id: str) -> None:
    _service().remove(event_id, user_id)


@router.put("", response_model=list[RegistrationDetail])
async def save_registrations(event_id: str, body: list[RegistrationCreate]) -> list[RegistrationDetail]:
    return _service().replace_all(event_id, body)


@router.patch("/{user_id}", response_model=RegistrationDetail)
async def update_registration(event_id: str, user_id: str, body: RegistrationUpdate) -> RegistrationDetail:
    result = _service().update(event_id, user_id, body)
    await manager.broadcast_refresh(event_id)
    return result
