from app.repositories.event_repository import EventRepository
from app.repositories.user_repository import UserRepository
from app.schemas.events import ScheduleEntry, ScheduleResponse


class ScheduleService:
    """Builds the public schedule response for an event."""

    def compute(self, event_id: str) -> ScheduleResponse:
        event_repo = EventRepository()
        user_repo = UserRepository()

        event = event_repo.load(event_id)
        entries: list[ScheduleEntry] = []

        for reg in event.registrations:
            user = user_repo.find_by_id(reg.user_id)
            if user is None:
                continue
            initial = f"{user.last_name[0].upper()}." if user.last_name else ""
            entries.append(
                ScheduleEntry(
                    first_name=user.first_name,
                    last_name_initial=initial,
                    phone=user.phone,
                    start_time_planned=reg.start_time_planned,
                )
            )

        # Sort by start_time_planned ascending, nulls last
        entries.sort(key=lambda e: (e.start_time_planned is None, e.start_time_planned or ""))

        return ScheduleResponse(event_name=event.name, entries=entries)

