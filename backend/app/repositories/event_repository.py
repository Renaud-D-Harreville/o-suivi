import json
from pathlib import Path

from app.config import DATA_DIR
from app.domain.exceptions import EntityNotFound
from app.schemas.events import EventBeacon, EventDetail, EventRegistration, EventSummary, EventUpdate
from app.schemas.templates import Gate, TemplateImportData


class EventRepository:
    """Encapsulates event file access. Returns typed objects only."""

    _events_dir = DATA_DIR / "events"

    def list_all(self) -> list[EventSummary]:
        self._events_dir.mkdir(parents=True, exist_ok=True)
        events: list[EventSummary] = []
        for event_dir in sorted(self._events_dir.iterdir()):
            event_file = event_dir / "event.json"
            if event_file.exists():
                with event_file.open() as f:
                    data = json.load(f)
                events.append(EventSummary(id=data["id"], name=data["name"], date=data.get("date")))
        return events

    def create(self, event_id: str, name: str) -> EventSummary:
        self._events_dir.mkdir(parents=True, exist_ok=True)
        event_data = {
            "id": event_id,
            "name": name,
            "date": None,
            "template_id": None,
            "first_start_time": None,
            "routechoices_url": None,
            "routechoices_event_id": None,
            "gps_polling_enabled": False,
            "start_mode": None,
            "beacons": [],
            "courses": [],
            "time_gates": [],
            "registrations": [],
        }
        event_dir = self._events_dir / event_id
        event_dir.mkdir(parents=True, exist_ok=True)
        (event_dir / "logs").mkdir(exist_ok=True)
        self._write_raw(event_id, event_data)
        return EventSummary(id=event_id, name=name, date=None)

    def load(self, event_id: str) -> EventDetail:
        data = self._read_raw(event_id)
        data["courses"] = self._enrich_courses(data.get("beacons", []), data.get("courses", []))
        return EventDetail(**data)

    def update(self, event_id: str, updates: EventUpdate) -> EventDetail:
        data = self._read_raw(event_id)
        data.update(updates.model_dump(exclude_unset=True))
        self._write_raw(event_id, data)
        data["courses"] = self._enrich_courses(data.get("beacons", []), data.get("courses", []))
        return EventDetail(**data)

    def import_template(self, event_id: str, template_data: TemplateImportData) -> EventDetail:
        """Copy beacons, courses and time_gates from template data into event."""
        data = self._read_raw(event_id)
        data["beacons"] = [{**b.model_dump(), "code": ""} for b in template_data.beacons]
        data["courses"] = [c.model_dump() for c in template_data.courses]
        data["time_gates"] = [tg.model_dump() for tg in template_data.time_gates]
        self._write_raw(event_id, data)
        data["courses"] = self._enrich_courses(data.get("beacons", []), data.get("courses", []))
        return EventDetail(**data)

    def get_course_beacons(self, event: EventDetail, course_number: int | None) -> list[EventBeacon]:
        if course_number is None:
            return []
        beacon_map = {b.id: b for b in event.beacons}
        for course in event.courses:
            if course.number == course_number:
                return [beacon_map[b.id] for b in course.beacons if b.id in beacon_map]
        return []

    def get_time_gates(self, event: EventDetail, course_number: int | None) -> list[Gate]:
        if course_number is None:
            return []
        for tg in event.time_gates:
            if tg.course_number == course_number:
                return tg.gates
        return []

    def get_registrations(self, event_id: str) -> list[EventRegistration]:
        """Return typed registrations for an event."""
        data = self._read_raw(event_id)
        return [EventRegistration(**r) for r in data.get("registrations", [])]

    def set_registrations(self, event_id: str, registrations: list[EventRegistration]) -> None:
        """Replace registrations in event and persist."""
        data = self._read_raw(event_id)
        data["registrations"] = [r.model_dump() for r in registrations]
        self._write_raw(event_id, data)

    def set_routechoices_event_id(self, event_id: str, routechoices_event_id: str) -> EventDetail:
        """Persist Routechoices event id and return enriched event detail."""
        data = self._read_raw(event_id)
        data["routechoices_event_id"] = routechoices_event_id
        self._write_raw(event_id, data)
        data["courses"] = self._enrich_courses(data.get("beacons", []), data.get("courses", []))
        return EventDetail(**data)

    def _read_raw(self, event_id: str) -> dict:
        """Read raw event JSON. Internal only."""
        event_file = self._event_file(event_id)
        if not event_file.exists():
            raise EntityNotFound("Event", event_id)
        with event_file.open() as f:
            return json.load(f)

    def _write_raw(self, event_id: str, data: dict) -> None:
        """Write raw event JSON."""
        event_file = self._event_file(event_id)
        with event_file.open("w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _event_file(self, event_id: str) -> Path:
        return self._events_dir / event_id / "event.json"

    @staticmethod
    def _enrich_courses(beacons: list[dict], courses: list[dict]) -> list[dict]:
        """Resolve beacon ids in courses to full Beacon objects."""
        beacon_map = {b["id"]: b for b in beacons}
        return [
            {
                "number": c["number"],
                "beacons": [
                    {
                        "id": beacon_map[bid]["id"],
                        "number": beacon_map[bid]["number"],
                        "tag": beacon_map[bid]["tag"],
                        "is_ph": beacon_map[bid].get("is_ph", False),
                        "code": beacon_map[bid].get("code", ""),
                        "coordinates": beacon_map[bid].get("coordinates"),
                    }
                    for bid in c.get("beacons", [])
                    if bid in beacon_map
                ],
            }
            for c in courses
        ]

