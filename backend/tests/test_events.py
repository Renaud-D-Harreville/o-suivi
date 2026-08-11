from fastapi.testclient import TestClient

from app.config import DATA_DIR
from app.main import app
from app.schemas.routechoices import RoutechoicesCompetitorRaw, RoutechoicesEventDataRaw
from app.services.routechoices_service import RoutechoicesService

client = TestClient(app)


def _get_token() -> str:
    response = client.post(
        "/api/auth/login",
        json={"username": "renaud", "password": "arvik"},
    )
    return response.json()["token"]



def test_list_events_empty() -> None:
    token = _get_token()
    response = client.get("/api/events", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == []


def test_create_event() -> None:
    token = _get_token()
    response = client.post(
        "/api/events",
        json={"name": "Proba Blanc Septembre"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Proba Blanc Septembre"
    assert "id" in data
    assert data["date"] is None


def test_create_event_then_list() -> None:
    token = _get_token()
    client.post(
        "/api/events",
        json={"name": "Event A"},
        headers={"Authorization": f"Bearer {token}"},
    )
    client.post(
        "/api/events",
        json={"name": "Event B"},
        headers={"Authorization": f"Bearer {token}"},
    )
    response = client.get("/api/events", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    names = [e["name"] for e in response.json()]
    assert "Event A" in names
    assert "Event B" in names


def test_create_event_empty_name() -> None:
    token = _get_token()
    response = client.post(
        "/api/events",
        json={"name": ""},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422


def test_list_events_public_access() -> None:
    """GET /api/events should be accessible without authentication."""
    response = client.get("/api/events")
    assert response.status_code == 200


def test_create_event_requires_auth() -> None:
    response = client.post("/api/events", json={"name": "Test"})
    assert response.status_code == 401


def test_create_event_persists_file() -> None:
    token = _get_token()
    response = client.post(
        "/api/events",
        json={"name": "Persistent Event"},
        headers={"Authorization": f"Bearer {token}"},
    )
    event_id = response.json()["id"]
    events_dir = DATA_DIR / "events"
    event_file = events_dir / event_id / "event.json"
    assert event_file.exists()
    logs_dir = events_dir / event_id / "logs"
    assert logs_dir.exists()


def _create_event(token: str, name: str = "Test Event") -> str:
    """Helper: create an event and return its id."""
    response = client.post(
        "/api/events",
        json={"name": name},
        headers={"Authorization": f"Bearer {token}"},
    )
    return response.json()["id"]


def test_get_event_detail() -> None:
    token = _get_token()
    event_id = _create_event(token, "Proba Chartreuse")
    response = client.get(
        f"/api/events/{event_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == event_id
    assert data["name"] == "Proba Chartreuse"
    assert data["date"] is None
    assert data["template_id"] is None
    assert data["beacons"] == []
    assert data["courses"] == []
    assert data["registrations"] == []


def test_get_event_not_found() -> None:
    token = _get_token()
    response = client.get(
        "/api/events/nonexistent-id",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


def test_update_event_partial() -> None:
    token = _get_token()
    event_id = _create_event(token)
    response = client.patch(
        f"/api/events/{event_id}",
        json={"date": "2026-09-15", "first_start_time": "07:30"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["date"] == "2026-09-15"
    assert data["first_start_time"] == "07:30"
    assert data["name"] == "Test Event"  # unchanged


def test_update_event_name() -> None:
    token = _get_token()
    event_id = _create_event(token)
    response = client.patch(
        f"/api/events/{event_id}",
        json={"name": "Nouveau nom"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Nouveau nom"


def test_update_event_not_found() -> None:
    token = _get_token()
    response = client.patch(
        "/api/events/nonexistent-id",
        json={"name": "Nope"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


def test_update_event_persists() -> None:
    token = _get_token()
    event_id = _create_event(token)
    client.patch(
        f"/api/events/{event_id}",
        json={"date": "2026-10-01", "routechoices_url": "https://example.com"},
        headers={"Authorization": f"Bearer {token}"},
    )
    # Re-fetch to verify persistence
    response = client.get(
        f"/api/events/{event_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    data = response.json()
    assert data["date"] == "2026-10-01"
    assert data["routechoices_url"] == "https://example.com"


def test_update_event_persists_routechoices_event_id() -> None:
    token = _get_token()
    event_id = _create_event(token)
    client.patch(
        f"/api/events/{event_id}",
        json={"routechoices_event_id": "AAXESzM45fQ"},
        headers={"Authorization": f"Bearer {token}"},
    )
    response = client.get(
        f"/api/events/{event_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["routechoices_event_id"] == "AAXESzM45fQ"


def test_routechoices_gps_persists_resolved_event_id(monkeypatch) -> None:
    token = _get_token()
    event_id = _create_event(token)
    client.patch(
        f"/api/events/{event_id}",
        json={"routechoices_url": "https://arvik.routechoices.com/API-test/"},
        headers={"Authorization": f"Bearer {token}"},
    )

    monkeypatch.setattr(RoutechoicesService, "resolve_event_id", lambda _self, _event: "AAXESzM45fQ")
    monkeypatch.setattr(
        RoutechoicesService,
        "fetch_event_payload",
        lambda _self, _eid: RoutechoicesEventDataRaw(
            competitors=[RoutechoicesCompetitorRaw(id="comp_1", encoded_data="abc")],
            next=None,
        ),
    )

    response = client.get(
        f"/api/events/{event_id}/routechoices/gps",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["routechoices_event_id"] == "AAXESzM45fQ"
    assert response.json()["payload"]["competitors"][0]["id"] == "comp_1"

    updated = client.get(f"/api/events/{event_id}", headers={"Authorization": f"Bearer {token}"})
    assert updated.status_code == 200
    assert updated.json()["routechoices_event_id"] == "AAXESzM45fQ"


def test_routechoices_gps_uses_existing_event_id(monkeypatch) -> None:
    token = _get_token()
    event_id = _create_event(token)
    client.patch(
        f"/api/events/{event_id}",
        json={"routechoices_event_id": "KNOWN123"},
        headers={"Authorization": f"Bearer {token}"},
    )

    monkeypatch.setattr(
        RoutechoicesService,
        "fetch_event_payload",
        lambda _self, _eid: RoutechoicesEventDataRaw(
            competitors=[RoutechoicesCompetitorRaw(id=_eid, encoded_data="abc")],
            next=None,
        ),
    )

    response = client.get(
        f"/api/events/{event_id}/routechoices/gps",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["routechoices_event_id"] == "KNOWN123"
    assert response.json()["payload"]["competitors"][0]["id"] == "KNOWN123"


def test_get_event_requires_auth() -> None:
    response = client.get("/api/events/some-id")
    assert response.status_code == 401


def test_update_event_requires_auth() -> None:
    response = client.patch("/api/events/some-id", json={"name": "X"})
    assert response.status_code == 401


def test_update_event_beacons() -> None:
    token = _get_token()
    event_id = _create_event(token)
    beacons = [
        {"id": 31, "number": 1, "tag": "unique", "is_ph": False, "code": "AB", "coordinates": "45.883424, 5.863804"},
        {"id": 32, "number": 2, "tag": "NO", "is_ph": False, "code": "CD"},
        {"id": 33, "number": 3, "tag": "unique", "is_ph": True, "code": "EF"},
    ]
    response = client.patch(
        f"/api/events/{event_id}",
        json={"beacons": beacons},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["beacons"]) == 3
    assert data["beacons"][0]["code"] == "AB"
    assert data["beacons"][0]["id"] == 31
    assert data["beacons"][0]["coordinates"] == "45.883424, 5.863804"
    assert data["beacons"][1]["coordinates"] is None
    assert data["beacons"][2]["is_ph"] is True


def test_update_event_courses() -> None:
    token = _get_token()
    event_id = _create_event(token)
    # First set beacons so courses can reference them
    beacons = [
        {"id": 31, "number": 1, "tag": "unique", "is_ph": False, "code": "AB"},
        {"id": 32, "number": 2, "tag": "NO", "is_ph": False, "code": "CD"},
        {"id": 33, "number": 2, "tag": "SE", "is_ph": False, "code": "EF"},
    ]
    client.patch(
        f"/api/events/{event_id}",
        json={"beacons": beacons},
        headers={"Authorization": f"Bearer {token}"},
    )
    courses = [
        {"number": 1, "beacons": [31, 32]},
        {"number": 2, "beacons": [31, 33]},
    ]
    response = client.patch(
        f"/api/events/{event_id}",
        json={"courses": courses},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["courses"]) == 2
    # Courses are enriched in response
    assert data["courses"][0]["beacons"][1]["tag"] == "NO"
    assert data["courses"][1]["beacons"][1]["tag"] == "SE"


def test_update_event_time_gates() -> None:
    token = _get_token()
    event_id = _create_event(token)
    time_gates = [
        {
            "course_number": 1,
            "gates": [
                {"gate": "PH1", "min_m": 50, "max_m": 83, "min_f": 49, "max_f": 94},
            ],
        }
    ]
    response = client.patch(
        f"/api/events/{event_id}",
        json={"time_gates": time_gates},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["time_gates"][0]["gates"][0]["max_m"] == 83


def _create_template_with_data(token: str) -> str:
    """Helper: create a template with beacons, courses and time_gates."""
    response = client.post(
        "/api/templates",
        json={"name": "Test Template"},
        headers={"Authorization": f"Bearer {token}"},
    )
    tid = response.json()["id"]
    client.put(
        f"/api/templates/{tid}/beacons",
        json=[
            {"id": 31, "number": 1, "tag": "unique", "is_ph": False, "coordinates": "45.883424, 5.863804"},
            {"id": 32, "number": 2, "tag": "NO", "is_ph": False},
            {"id": 33, "number": 3, "tag": "unique", "is_ph": True},
        ],
        headers={"Authorization": f"Bearer {token}"},
    )
    client.put(
        f"/api/templates/{tid}/courses",
        json=[
            {"number": 1, "beacons": [31, 32, 33]},
        ],
        headers={"Authorization": f"Bearer {token}"},
    )
    client.put(
        f"/api/templates/{tid}/time-gates",
        json=[
            {"course_number": 1, "gates": [
                {"gate": "PH1", "min_m": 45, "max_m": 75, "min_f": 45, "max_f": 85},
            ]},
        ],
        headers={"Authorization": f"Bearer {token}"},
    )
    return tid


def test_import_template_success() -> None:
    token = _get_token()
    tid = _create_template_with_data(token)
    eid = _create_event(token)
    # Set template_id on event
    client.patch(
        f"/api/events/{eid}",
        json={"template_id": tid},
        headers={"Authorization": f"Bearer {token}"},
    )
    # Import
    response = client.post(
        f"/api/events/{eid}/import-template",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["beacons"]) == 3
    assert data["beacons"][0]["code"] == ""
    assert data["beacons"][0]["tag"] == "unique"
    assert data["beacons"][0]["id"] == 31
    assert data["beacons"][0]["coordinates"] == "45.883424, 5.863804"
    assert len(data["courses"]) == 1
    assert len(data["time_gates"]) == 1
    # Courses are enriched
    assert data["courses"][0]["beacons"][0]["tag"] == "unique"


def test_import_template_no_template_selected() -> None:
    token = _get_token()
    eid = _create_event(token)
    response = client.post(
        f"/api/events/{eid}/import-template",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400
    assert "No template selected" in response.json()["detail"]


def test_import_template_overwrites_existing() -> None:
    token = _get_token()
    tid = _create_template_with_data(token)
    eid = _create_event(token)
    # Set template + existing beacons with codes
    client.patch(
        f"/api/events/{eid}",
        json={
            "template_id": tid,
            "beacons": [{"id": 99, "number": 99, "tag": "unique", "is_ph": False, "code": "ZZ"}],
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    # Import should overwrite
    response = client.post(
        f"/api/events/{eid}/import-template",
        headers={"Authorization": f"Bearer {token}"},
    )
    data = response.json()
    assert len(data["beacons"]) == 3  # template has 3, not 1
    assert all(b["code"] == "" for b in data["beacons"])


def test_import_template_requires_auth() -> None:
    response = client.post("/api/events/some-id/import-template")
    assert response.status_code == 401
