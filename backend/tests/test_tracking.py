import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
_DATA_DIR = Path(__file__).resolve().parent / "resources" / "data"


def _get_token() -> str:
    resp = client.post("/api/auth/login", json={"username": "renaud", "password": "arvik"})
    return resp.json()["token"]


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _create_event(token: str) -> str:
    resp = client.post("/api/events", json={"name": "Tracking Test"}, headers=_headers(token))
    event_id = resp.json()["id"]
    client.patch(
        f"/api/events/{event_id}",
        json={
            "beacons": [
                {"id": 31, "number": 1, "tag": "unique", "is_ph": False, "code": "AB"},
                {"id": 32, "number": 2, "tag": "unique", "is_ph": True, "code": "CD"},
                {"id": 33, "number": 3, "tag": "unique", "is_ph": False, "code": "EF"},
                {"id": 34, "number": 4, "tag": "unique", "is_ph": True, "code": "GH"},
            ],
            "courses": [{"number": 1, "beacons": [31, 32, 33, 34]}],
            "time_gates": [{"course_number": 1, "gates": [
                {"gate": "PH1", "min_m": 30, "max_m": 60, "min_f": 30, "max_f": 70},
                {"gate": "PH2", "min_m": 20, "max_m": 45, "min_f": 20, "max_f": 55},
            ]}],
        },
        headers=_headers(token),
    )
    return event_id


def _register(token: str, event_id: str, first: str = "Marie", last: str = "Dupont", sex: str = "F") -> str:
    resp = client.post(
        f"/api/events/{event_id}/registrations",
        json={"first_name": first, "last_name": last, "sex": sex, "phone": "0612345678"},
        headers=_headers(token),
    )
    uid = resp.json()["user_id"]
    client.patch(f"/api/events/{event_id}/registrations/{uid}", json={"course_number": 1}, headers=_headers(token))
    return uid


def _write_logs(event_id: str, user_id: str, logs: list[dict]) -> None:
    log_dir = _DATA_DIR / "events" / event_id / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / f"{user_id}.json").write_text(json.dumps(logs, indent=2))


# --- Tests ---


def test_tracking_empty_event() -> None:
    token = _get_token()
    eid = _create_event(token)
    resp = client.get(f"/api/events/{eid}/tracking", headers=_headers(token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Tracking Test"
    assert data["competitors"] == []
    assert len(data["courses"]) == 1
    assert len(data["time_gates"]) == 1
    assert len(data["beacons"]) == 4


def test_tracking_with_competitors() -> None:
    token = _get_token()
    eid = _create_event(token)
    uid = _register(token, eid)

    resp = client.get(f"/api/events/{eid}/tracking", headers=_headers(token))
    data = resp.json()
    assert len(data["competitors"]) == 1

    comp = data["competitors"][0]
    assert comp["user_id"] == uid
    assert comp["first_name"] == "Marie"
    assert comp["last_name"] == "Dupont"
    assert comp["sex"] == "F"
    assert comp["phone"] == "0612345678"
    assert comp["course_number"] == 1
    assert comp["departed"] is False
    assert comp["dns"] is False
    assert comp["abandoned"] is False
    assert comp["tracker_returned"] is False


def test_tracking_departed_competitor() -> None:
    token = _get_token()
    eid = _create_event(token)
    uid = _register(token, eid)
    _write_logs(eid, uid, [
        {"log_type": "departure", "metadata": {"creation_date": "2026-09-15T07:00:00", "received_at": "2026-09-15T07:00:01Z", "author_id": "usr_001"}},
    ])

    resp = client.get(f"/api/events/{eid}/tracking", headers=_headers(token))
    comp = resp.json()["competitors"][0]
    assert comp["departed"] is True
    assert comp["departure_time"] == "07:00:00"


def test_tracking_dns_competitor() -> None:
    token = _get_token()
    eid = _create_event(token)
    uid = _register(token, eid)
    _write_logs(eid, uid, [
        {"log_type": "dns", "metadata": {"creation_date": "2026-09-15T07:00:00Z", "received_at": "2026-09-15T07:00:01Z", "author_id": "usr_001"}, "data": {"comment": "Absent"}},
    ])

    resp = client.get(f"/api/events/{eid}/tracking", headers=_headers(token))
    comp = resp.json()["competitors"][0]
    assert comp["dns"] is True


def test_tracking_with_checkpoints() -> None:
    token = _get_token()
    eid = _create_event(token)
    uid = _register(token, eid)
    _write_logs(eid, uid, [
        {"log_type": "departure", "metadata": {"creation_date": "2026-09-15T07:00:00", "received_at": "2026-09-15T07:00:01Z", "author_id": "usr_001"}},
        {"log_type": "checkpoint_edit", "metadata": {"creation_date": "2026-09-15T07:10:00", "received_at": "2026-09-15T07:10:01Z", "author_id": "usr_001"}, "data": {"sequence": 1, "code": "AB", "passage_time": "2026-09-15T07:10:00"}},
        {"log_type": "checkpoint_edit", "metadata": {"creation_date": "2026-09-15T07:30:00", "received_at": "2026-09-15T07:30:01Z", "author_id": "usr_001"}, "data": {"sequence": 2, "code": "CD", "passage_time": "2026-09-15T07:30:00"}},
    ])

    resp = client.get(f"/api/events/{eid}/tracking", headers=_headers(token))
    comp = resp.json()["competitors"][0]
    assert len(comp["checkpoints"]) == 2
    assert comp["checkpoints"][0]["sequence"] in [1, 2]
    assert comp["departed"] is True


def test_tracking_abandoned_and_tracker() -> None:
    token = _get_token()
    eid = _create_event(token)
    uid = _register(token, eid)
    _write_logs(eid, uid, [
        {"log_type": "departure", "metadata": {"creation_date": "2026-09-15T07:00:00", "received_at": "2026-09-15T07:00:01Z", "author_id": "usr_001"}},
        {"log_type": "abandon", "metadata": {"creation_date": "2026-09-15T07:30:00", "received_at": "2026-09-15T07:30:01Z", "author_id": "usr_001"}, "data": {"comment": "Injury"}},
        {"log_type": "tracker_returned", "metadata": {"creation_date": "2026-09-15T07:35:00", "received_at": "2026-09-15T07:35:01Z", "author_id": "usr_001"}, "data": {"tracker_number": "T42"}},
    ])

    resp = client.get(f"/api/events/{eid}/tracking", headers=_headers(token))
    comp = resp.json()["competitors"][0]
    assert comp["abandoned"] is True
    assert comp["tracker_returned"] is True


def test_tracking_logs_included() -> None:
    token = _get_token()
    eid = _create_event(token)
    uid = _register(token, eid)
    _write_logs(eid, uid, [
        {"log_type": "departure", "metadata": {"creation_date": "2026-09-15T07:00:00", "received_at": "2026-09-15T07:00:01Z", "author_id": "usr_001"}},
    ])

    resp = client.get(f"/api/events/{eid}/tracking", headers=_headers(token))
    comp = resp.json()["competitors"][0]
    assert len(comp["logs"]) == 1
    assert comp["logs"][0]["log_type"] == "departure"


def test_tracking_requires_auth() -> None:
    resp = client.get("/api/events/fake-id/tracking")
    assert resp.status_code == 401


def test_tracking_multiple_competitors() -> None:
    token = _get_token()
    eid = _create_event(token)
    uid1 = _register(token, eid, "Alice", "Martin", "F")
    uid2 = _register(token, eid, "Bob", "Durand", "H")

    _write_logs(eid, uid1, [
        {"log_type": "departure", "metadata": {"creation_date": "2026-09-15T07:00:00", "received_at": "2026-09-15T07:00:01Z", "author_id": "usr_001"}},
    ])

    resp = client.get(f"/api/events/{eid}/tracking", headers=_headers(token))
    data = resp.json()
    assert len(data["competitors"]) == 2
    departed_ids = [c["user_id"] for c in data["competitors"] if c["departed"]]
    assert uid1 in departed_ids
    not_departed_ids = [c["user_id"] for c in data["competitors"] if not c["departed"]]
    assert uid2 in not_departed_ids


def test_tracking_courses_include_beacon_code() -> None:
    """Enriched course beacons must carry the 'code' field for frontend validation."""
    token = _get_token()
    eid = _create_event(token)

    resp = client.get(f"/api/events/{eid}/tracking", headers=_headers(token))
    data = resp.json()
    course = data["courses"][0]
    for beacon in course["beacons"]:
        assert "code" in beacon
    codes = [b["code"] for b in course["beacons"]]
    assert "AB" in codes
    assert "CD" in codes
    assert "EF" in codes
    assert "GH" in codes


def test_tracking_logs_include_author_name() -> None:
    """Log entries in tracking response must have author_name resolved."""
    token = _get_token()
    eid = _create_event(token)

    # Get the organizer's user_id from token
    resp = client.post("/api/auth/login", json={"username": "renaud", "password": "arvik"})
    organizer_id = resp.json().get("user_id", "")

    uid = _register(token, eid)
    _write_logs(eid, uid, [
        {"log_type": "departure", "metadata": {"creation_date": "2026-09-15T07:00:00", "received_at": "2026-09-15T07:00:01Z", "author_id": organizer_id}},
        {"log_type": "checkpoint_edit", "metadata": {"creation_date": "2026-09-15T07:10:00", "received_at": "2026-09-15T07:10:01Z", "author_id": "public"}, "data": {"sequence": 1, "code": "AB", "passage_time": "2026-09-15T07:10:00"}},
    ])

    resp = client.get(f"/api/events/{eid}/tracking", headers=_headers(token))
    comp = resp.json()["competitors"][0]
    logs = comp["logs"]
    assert len(logs) == 2

    # First log: organizer — name should be resolved (non-empty)
    assert logs[0]["metadata"]["author_name"] != ""

    # Second log: public — should be "public"
    assert logs[1]["metadata"]["author_name"] == "public"


