import json

from app.config import DATA_DIR
from app.domain.exceptions import EntityNotFound
from app.schemas.templates import (
    Beacon,
    Course,
    CourseDetail,
    CourseTimeGates,
    TemplateImportData,
    TemplateSummary,
)


class TemplateRepository:
    """Encapsulates template file access. Returns typed objects only."""

    _templates_dir = DATA_DIR / "templates"

    def list_all(self) -> list[TemplateSummary]:
        self._templates_dir.mkdir(parents=True, exist_ok=True)
        templates: list[TemplateSummary] = []
        for file in sorted(self._templates_dir.glob("*.json")):
            with file.open() as f:
                data = json.load(f)
            templates.append(TemplateSummary(id=data["id"], name=data["name"]))
        return templates

    def load(self, template_id: str) -> TemplateSummary:
        data = self._read_raw(template_id)
        return TemplateSummary(id=data["id"], name=data["name"])

    def create(self, template_id: str, name: str) -> TemplateSummary:
        self._templates_dir.mkdir(parents=True, exist_ok=True)
        data = {
            "id": template_id,
            "name": name,
            "beacons": [],
            "courses": [],
            "time_gates": [],
        }
        self._write_raw(template_id, data)
        return TemplateSummary(id=template_id, name=name)

    def update_name(self, template_id: str, name: str) -> TemplateSummary:
        data = self._read_raw(template_id)
        data["name"] = name
        self._write_raw(template_id, data)
        return TemplateSummary(id=data["id"], name=data["name"])

    def get_beacons(self, template_id: str) -> list[Beacon]:
        data = self._read_raw(template_id)
        return [Beacon(**b) for b in data.get("beacons", [])]

    def replace_beacons(self, template_id: str, beacons: list[Beacon]) -> list[Beacon]:
        data = self._read_raw(template_id)
        data["beacons"] = [b.model_dump() for b in beacons]
        self._write_raw(template_id, data)
        return beacons

    def get_courses(self, template_id: str) -> list[CourseDetail]:
        data = self._read_raw(template_id)
        enriched = self._enrich_courses(data.get("beacons", []), data.get("courses", []))
        return [CourseDetail(**c) for c in enriched]

    def replace_courses(self, template_id: str, courses: list[Course]) -> list[CourseDetail]:
        data = self._read_raw(template_id)
        data["courses"] = [c.model_dump() for c in courses]
        self._write_raw(template_id, data)
        enriched = self._enrich_courses(data.get("beacons", []), data["courses"])
        return [CourseDetail(**c) for c in enriched]

    def get_time_gates(self, template_id: str) -> list[CourseTimeGates]:
        data = self._read_raw(template_id)
        return [CourseTimeGates(**tg) for tg in data.get("time_gates", [])]

    def replace_time_gates(self, template_id: str, time_gates: list[CourseTimeGates]) -> list[CourseTimeGates]:
        data = self._read_raw(template_id)
        data["time_gates"] = [tg.model_dump() for tg in time_gates]
        self._write_raw(template_id, data)
        return time_gates

    def get_import_data(self, template_id: str) -> TemplateImportData:
        """Return typed template data for event import (beacons, courses, time_gates)."""
        data = self._read_raw(template_id)
        return TemplateImportData(
            beacons=[Beacon(**b) for b in data.get("beacons", [])],
            courses=[Course(**c) for c in data.get("courses", [])],
            time_gates=[CourseTimeGates(**tg) for tg in data.get("time_gates", [])],
        )

    def _read_raw(self, template_id: str) -> dict:
        """Read raw JSON data. Internal only — never exposed to callers."""
        file_path = self._templates_dir / f"{template_id}.json"
        if not file_path.exists():
            raise EntityNotFound("Template", template_id)
        with file_path.open() as f:
            return json.load(f)

    def _write_raw(self, template_id: str, data: dict) -> None:
        """Write raw JSON data to file."""
        file_path = self._templates_dir / f"{template_id}.json"
        with file_path.open("w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def _enrich_courses(beacons: list[dict], courses: list[dict]) -> list[dict]:
        """Resolve beacon ids in courses to full Beacon objects."""
        beacon_map = {b["id"]: b for b in beacons}
        return [
            {
                "number": course["number"],
                "beacons": [
                    {
                        "id": beacon_map[bid]["id"],
                        "number": beacon_map[bid]["number"],
                        "tag": beacon_map[bid]["tag"],
                        "is_ph": beacon_map[bid].get("is_ph", False),
                    }
                    for bid in course.get("beacons", [])
                    if bid in beacon_map
                ],
            }
            for course in courses
        ]

