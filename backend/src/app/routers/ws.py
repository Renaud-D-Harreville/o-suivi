from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from jose import JWTError, jwt

from app.config import JWT_SECRET, JWT_ALGORITHM
from app.websocket.connection_manager import manager

router = APIRouter(tags=["websocket"])


@router.websocket("/api/events/{event_id}/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    event_id: str,
    token: str = Query(),
) -> None:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("role") != "organizer":
            await websocket.close(code=4003)
            return
    except JWTError:
        await websocket.close(code=4001)
        return

    await manager.connect(event_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(event_id, websocket)

