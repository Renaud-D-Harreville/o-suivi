"""Background asyncio task that runs GPS polling every 60 seconds."""

from __future__ import annotations

import asyncio
import logging

from app.services.gps_polling_service import GpsPollingService

logger = logging.getLogger(__name__)

_POLL_INTERVAL_S = 60
_task: asyncio.Task[None] | None = None


async def _polling_loop() -> None:
    """Infinite loop: poll once, then sleep."""
    service = GpsPollingService()
    logger.info("GPS polling loop running")
    while True:
        try:
            await service.poll_once()
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("GPS polling cycle failed")
        await asyncio.sleep(_POLL_INTERVAL_S)


async def start_polling() -> None:
    """Start the background polling task (idempotent)."""
    global _task  # noqa: PLW0603
    if _task is None or _task.done():
        _task = asyncio.create_task(_polling_loop())
        logger.info("GPS polling task started (interval=%ds)", _POLL_INTERVAL_S)


def stop_polling() -> None:
    """Cancel the background polling task."""
    global _task  # noqa: PLW0603
    if _task and not _task.done():
        _task.cancel()
        logger.info("GPS polling task stopped")
    _task = None


