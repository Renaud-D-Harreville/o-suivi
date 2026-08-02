import json
from pathlib import Path

from pydantic import TypeAdapter

from app.config import DATA_DIR
from app.schemas.logs import BaseLogEntry, LogEntry

_LOG_LIST_ADAPTER = TypeAdapter(list[LogEntry])


class LogRepository:
    """Loads and appends competitor log entries as typed objects."""

    _events_dir = DATA_DIR / "events"

    def load(self, event_id: str, user_id: str) -> list[LogEntry]:
        log_file = self._log_file(event_id, user_id)
        if not log_file.exists():
            return []
        with log_file.open() as f:
            raw = json.load(f)
        raw.sort(key=lambda e: e.get("metadata", {}).get("creation_date", ""))
        return _LOG_LIST_ADAPTER.validate_python(raw)

    def append(self, event_id: str, user_id: str, entry: BaseLogEntry) -> None:
        """Append a typed log entry to the user's log file."""
        log_file = self._log_file(event_id, user_id)
        if log_file.exists():
            with log_file.open() as f:
                logs = json.load(f)
        else:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            logs = []
        logs.append(entry.model_dump())
        with log_file.open("w") as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)

    def _log_file(self, event_id: str, user_id: str) -> Path:
        return self._events_dir / event_id / "logs" / f"{user_id}.json"

