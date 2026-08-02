from fastapi import APIRouter, Depends

from app.dependencies import require_organizer
from app.schemas.results import ResultsResponse
from app.services.results_service import ResultsService

router = APIRouter(
    prefix="/api/events/{event_id}",
    tags=["results"],
    dependencies=[Depends(require_organizer)],
)


@router.get("/resultats", response_model=ResultsResponse)
async def get_results(event_id: str) -> ResultsResponse:
    service = ResultsService()
    return service.compute(event_id)

