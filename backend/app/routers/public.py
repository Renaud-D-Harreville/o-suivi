from fastapi import APIRouter

from app.schemas.logs import (
    CheckpointEditData,
    CheckpointEditLog,
    CheckpointEditRequest,
    PhArrivalEditData,
    PhArrivalEditLog,
    PhArrivalEditRequest,
)
from app.schemas.results import ResultsResponse
from app.schemas.splits import SplitsResponse
from app.services.checkpoint_service import CheckpointResponse, CheckpointService
from app.services.log_service import LogService
from app.services.results_service import ResultsService
from app.services.split_service import SplitService

router = APIRouter(
    prefix="/api/public/events/{event_id}",
    tags=["public"],
)

PUBLIC_AUTHOR_ID = "public"


@router.get("/resultats", response_model=ResultsResponse)
async def get_public_results(event_id: str) -> ResultsResponse:
    return ResultsService().compute(event_id)


@router.get("/splits", response_model=SplitsResponse)
async def get_public_splits(event_id: str) -> SplitsResponse:
    return SplitService().compute(event_id)


@router.get(
    "/competitors/{user_id}/checkpoints",
    response_model=CheckpointResponse,
)
async def get_public_checkpoints(event_id: str, user_id: str) -> CheckpointResponse:
    return CheckpointService().get_checkpoints_with_arrivals(event_id, user_id)


@router.post(
    "/competitors/{user_id}/checkpoint-edit",
    response_model=CheckpointEditLog,
    status_code=201,
)
async def public_checkpoint_edit(
    event_id: str,
    user_id: str,
    body: CheckpointEditRequest,
) -> CheckpointEditLog:
    svc = LogService()
    entry = CheckpointEditLog(
        metadata=svc.build_metadata(body.creation_date, PUBLIC_AUTHOR_ID),
        data=CheckpointEditData(
            sequence=body.sequence,
            code=body.code,
            passage_time=body.passage_time,
            comment=body.comment,
        ),
    )
    await svc.append_and_notify(event_id, user_id, entry)
    return entry


@router.post(
    "/competitors/{user_id}/ph-arrival-edit",
    response_model=PhArrivalEditLog,
    status_code=201,
)
async def public_ph_arrival_edit(
    event_id: str,
    user_id: str,
    body: PhArrivalEditRequest,
) -> PhArrivalEditLog:
    svc = LogService()
    entry = PhArrivalEditLog(
        metadata=svc.build_metadata(body.creation_date, PUBLIC_AUTHOR_ID),
        data=PhArrivalEditData(
            sequence=body.sequence,
            passage_time=body.passage_time,
        ),
    )
    await svc.append_and_notify(event_id, user_id, entry)
    return entry

