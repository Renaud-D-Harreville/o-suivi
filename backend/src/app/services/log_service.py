from datetime import datetime, timezone

from app.repositories.log_repository import LogRepository
from app.schemas.logs import BaseLogEntry, LogEntry, LogMetadata
from app.websocket.connection_manager import manager


class LogService:
    """Creates log entries and persists them. Shared by admin and public routers."""

    def __init__(self, logs: LogRepository | None = None) -> None:
        self._logs = logs or LogRepository()

    def build_metadata(self, creation_date: str, author_id: str) -> LogMetadata:
        """Build metadata with server-side received_at timestamp."""
        return LogMetadata(
            creation_date=creation_date,
            received_at=self._now_iso(),
            author_id=author_id,
        )

    async def append_and_notify(self, event_id: str, user_id: str, entry: BaseLogEntry) -> None:
        """Persist a log entry and broadcast refresh via WebSocket."""
        self._logs.append(event_id, user_id, entry)
        await manager.broadcast_refresh(event_id)

    def load(self, event_id: str, user_id: str) -> list[LogEntry]:
        """Load all logs for a competitor."""
        return self._logs.load(event_id, user_id)

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).isoformat(timespec="seconds")

