from fastapi import APIRouter, Depends

from app.dependencies import require_organizer
from app.schemas.auth import TokenPayload
from app.schemas.logs import (
    AbandonCancelLog,
    AbandonCancelRequest,
    AbandonLog,
    AbandonRequest,
    BagWeightData,
    BagWeightLog,
    BagWeightRequest,
    CheckpointEditData,
    CheckpointEditLog,
    CheckpointEditRequest,
    CommentData,
    DepartureCancelLog,
    DepartureCancelRequest,
    DepartureData,
    DepartureEditData,
    DepartureEditLog,
    DepartureEditRequest,
    DepartureLog,
    DepartureRequest,
    DnsCancelLog,
    DnsCancelRequest,
    DnsLog,
    DnsRequest,
    LogEntry,
    PhArrivalEditData,
    PhArrivalEditLog,
    PhArrivalEditRequest,
    TrackerReturnedCancelLog,
    TrackerReturnedCancelRequest,
    TrackerReturnedData,
    TrackerReturnedLog,
    TrackerReturnedRequest,
)
from app.services.log_service import LogService

router = APIRouter(
    prefix="/api/events/{event_id}/registrations/{user_id}",
    tags=["logs"],
)


def _service() -> LogService:
    return LogService()


@router.post("/depart", response_model=DepartureLog, status_code=201)
async def confirm_departure(
    event_id: str,
    user_id: str,
    body: DepartureRequest,
    current_user: TokenPayload = Depends(require_organizer),
) -> DepartureLog:
    svc = _service()
    entry = DepartureLog(
        metadata=svc.build_metadata(body.creation_date, current_user.user_id),
        data=DepartureData(departure_time=body.departure_time),
    )
    await svc.append_and_notify(event_id, user_id, entry)
    return entry


@router.post("/depart-cancel", response_model=DepartureCancelLog, status_code=201)
async def cancel_departure(
    event_id: str,
    user_id: str,
    body: DepartureCancelRequest,
    current_user: TokenPayload = Depends(require_organizer),
) -> DepartureCancelLog:
    svc = _service()
    entry = DepartureCancelLog(metadata=svc.build_metadata(body.creation_date, current_user.user_id))
    await svc.append_and_notify(event_id, user_id, entry)
    return entry


@router.post("/depart-edit", response_model=DepartureEditLog, status_code=201)
async def edit_departure_time(
    event_id: str,
    user_id: str,
    body: DepartureEditRequest,
    current_user: TokenPayload = Depends(require_organizer),
) -> DepartureEditLog:
    svc = _service()
    entry = DepartureEditLog(
        metadata=svc.build_metadata(body.creation_date, current_user.user_id),
        data=DepartureEditData(departure_time=body.departure_time),
    )
    await svc.append_and_notify(event_id, user_id, entry)
    return entry


@router.post("/dns", response_model=DnsLog, status_code=201)
async def mark_dns(
    event_id: str,
    user_id: str,
    body: DnsRequest,
    current_user: TokenPayload = Depends(require_organizer),
) -> DnsLog:
    svc = _service()
    entry = DnsLog(
        metadata=svc.build_metadata(body.creation_date, current_user.user_id),
        data=CommentData(comment=body.comment),
    )
    await svc.append_and_notify(event_id, user_id, entry)
    return entry


@router.post("/dns-cancel", response_model=DnsCancelLog, status_code=201)
async def cancel_dns(
    event_id: str,
    user_id: str,
    body: DnsCancelRequest,
    current_user: TokenPayload = Depends(require_organizer),
) -> DnsCancelLog:
    svc = _service()
    entry = DnsCancelLog(
        metadata=svc.build_metadata(body.creation_date, current_user.user_id),
        data=CommentData(comment=body.comment),
    )
    await svc.append_and_notify(event_id, user_id, entry)
    return entry


@router.post("/bag-weight", response_model=BagWeightLog, status_code=201)
async def record_bag_weight(
    event_id: str,
    user_id: str,
    body: BagWeightRequest,
    current_user: TokenPayload = Depends(require_organizer),
) -> BagWeightLog:
    svc = _service()
    entry = BagWeightLog(
        metadata=svc.build_metadata(body.creation_date, current_user.user_id),
        data=BagWeightData(moment=body.moment, weight_kg=body.weight_kg),
    )
    await svc.append_and_notify(event_id, user_id, entry)
    return entry


@router.post("/abandon", response_model=AbandonLog, status_code=201)
async def mark_abandon(
    event_id: str,
    user_id: str,
    body: AbandonRequest,
    current_user: TokenPayload = Depends(require_organizer),
) -> AbandonLog:
    svc = _service()
    entry = AbandonLog(
        metadata=svc.build_metadata(body.creation_date, current_user.user_id),
        data=CommentData(comment=body.comment),
    )
    await svc.append_and_notify(event_id, user_id, entry)
    return entry


@router.post("/abandon-cancel", response_model=AbandonCancelLog, status_code=201)
async def cancel_abandon(
    event_id: str,
    user_id: str,
    body: AbandonCancelRequest,
    current_user: TokenPayload = Depends(require_organizer),
) -> AbandonCancelLog:
    svc = _service()
    entry = AbandonCancelLog(
        metadata=svc.build_metadata(body.creation_date, current_user.user_id),
        data=CommentData(comment=body.comment),
    )
    await svc.append_and_notify(event_id, user_id, entry)
    return entry


@router.post("/tracker-returned", response_model=TrackerReturnedLog, status_code=201)
async def mark_tracker_returned(
    event_id: str,
    user_id: str,
    body: TrackerReturnedRequest,
    current_user: TokenPayload = Depends(require_organizer),
) -> TrackerReturnedLog:
    svc = _service()
    entry = TrackerReturnedLog(
        metadata=svc.build_metadata(body.creation_date, current_user.user_id),
        data=TrackerReturnedData(tracker_number=body.tracker_number),
    )
    await svc.append_and_notify(event_id, user_id, entry)
    return entry


@router.post(
    "/tracker-returned-cancel",
    response_model=TrackerReturnedCancelLog,
    status_code=201,
)
async def cancel_tracker_returned(
    event_id: str,
    user_id: str,
    body: TrackerReturnedCancelRequest,
    current_user: TokenPayload = Depends(require_organizer),
) -> TrackerReturnedCancelLog:
    svc = _service()
    entry = TrackerReturnedCancelLog(metadata=svc.build_metadata(body.creation_date, current_user.user_id))
    await svc.append_and_notify(event_id, user_id, entry)
    return entry


@router.post("/checkpoint-edit", response_model=CheckpointEditLog, status_code=201)
async def edit_checkpoint(
    event_id: str,
    user_id: str,
    body: CheckpointEditRequest,
    current_user: TokenPayload = Depends(require_organizer),
) -> CheckpointEditLog:
    svc = _service()
    entry = CheckpointEditLog(
        metadata=svc.build_metadata(body.creation_date, current_user.user_id),
        data=CheckpointEditData(
            sequence=body.sequence, code=body.code,
            passage_time=body.passage_time, comment=body.comment,
        ),
    )
    await svc.append_and_notify(event_id, user_id, entry)
    return entry


@router.post("/ph-arrival-edit", response_model=PhArrivalEditLog, status_code=201)
async def edit_ph_arrival(
    event_id: str,
    user_id: str,
    body: PhArrivalEditRequest,
    current_user: TokenPayload = Depends(require_organizer),
) -> PhArrivalEditLog:
    svc = _service()
    entry = PhArrivalEditLog(
        metadata=svc.build_metadata(body.creation_date, current_user.user_id),
        data=PhArrivalEditData(sequence=body.sequence, passage_time=body.passage_time),
    )
    await svc.append_and_notify(event_id, user_id, entry)
    return entry


@router.get("/logs", response_model=list[LogEntry])
async def get_logs(
    event_id: str,
    user_id: str,
) -> list[LogEntry]:
    return _service().load(event_id, user_id)
