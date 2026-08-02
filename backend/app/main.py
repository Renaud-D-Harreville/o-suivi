from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.requests import Request

from app.domain.exceptions import EntityNotFound
from app.routers.auth import router as auth_router
from app.routers.events import router as events_router
from app.routers.logs import router as logs_router
from app.routers.public import router as public_router
from app.routers.registrations import router as registrations_router
from app.routers.results import router as results_router
from app.routers.templates import router as templates_router
from app.routers.ws import router as ws_router
from app.schemas.common import HealthResponse

app = FastAPI(title="O-Suivi API", version="0.1.0")

app.include_router(auth_router)
app.include_router(templates_router)
app.include_router(events_router)
app.include_router(registrations_router)
app.include_router(logs_router)
app.include_router(results_router)
app.include_router(public_router)
app.include_router(ws_router)


@app.exception_handler(EntityNotFound)
async def entity_not_found_handler(request: Request, exc: EntityNotFound) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.get("/api/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(message="Hello World")
