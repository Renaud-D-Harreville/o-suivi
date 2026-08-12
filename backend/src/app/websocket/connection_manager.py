from fastapi import WebSocket


class ConnectionManager:
    """Manages WebSocket connections grouped by event_id."""

    def __init__(self) -> None:
        self._connections: dict[str, list[WebSocket]] = {}

    async def connect(self, event_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        if event_id not in self._connections:
            self._connections[event_id] = []
        self._connections[event_id].append(websocket)

    def disconnect(self, event_id: str, websocket: WebSocket) -> None:
        if event_id in self._connections:
            self._connections[event_id] = [
                ws for ws in self._connections[event_id] if ws is not websocket
            ]
            if not self._connections[event_id]:
                del self._connections[event_id]

    async def broadcast_refresh(self, event_id: str) -> None:
        """Notify all clients connected to this event that data has changed."""
        if event_id not in self._connections:
            return
        stale: list[WebSocket] = []
        for ws in self._connections[event_id]:
            try:
                await ws.send_json({"type": "refresh"})
            except Exception:
                stale.append(ws)
        for ws in stale:
            self.disconnect(event_id, ws)


manager = ConnectionManager()

