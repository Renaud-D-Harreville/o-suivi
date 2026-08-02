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
    resp = client.post("/api/events", json={"name": "Results Test"}, headers=_headers(token))
    event_id = resp.json()["id"]
    client.patch(
        f"/api/events/{event_id}",
        json={
            "beacons": [
                {"id": 31, "number": 1, "tag": "unique", "is_ph": False, "code": "AB"},
                {"id": 32, "number": 2, "tag": "unique", "is_ph": False, "code": "CD"},
                {"id": 33, "number": 3, "tag": "unique", "is_ph": True, "code": "EF"},
                {"id": 34, "number": 4, "tag": "unique", "is_ph": False, "code": "GH"},
                {"id": 35, "number": 5, "tag": "unique", "is_ph": True, "code": "IJ"},
            ],
            "courses": [{"number": 1, "beacons": [31, 32, 33, 34, 35]}],
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
        json={"first_name": first, "last_name": last, "sex": sex, "phone": ""},
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


def test_results_empty_event() -> None:
    token = _get_token()
    eid = _create_event(token)
    resp = client.get(f"/api/events/{eid}/resultats", headers=_headers(token))
    assert resp.status_code == 200
    assert resp.json()["competitors"] == []


def test_results_dns() -> None:
    token = _get_token()
    eid = _create_event(token)
    uid = _register(token, eid)
    _write_logs(eid, uid, [
        {"log_type": "dns", "metadata": {"creation_date": "2026-09-15T07:00:00Z", "received_at": "2026-09-15T07:00:01Z", "author_id": "usr_001"}, "data": {"comment": "Absent"}},
    ])
    resp = client.get(f"/api/events/{eid}/resultats", headers=_headers(token))
    comp = resp.json()["competitors"][0]
    assert comp["dns"] is True
    assert comp["valid_global"] is None


def test_results_full_valid_run() -> None:
    token = _get_token()
    eid = _create_event(token)
    uid = _register(token, eid)
    _write_logs(eid, uid, [
        {"log_type": "departure", "metadata": {"creation_date": "2026-09-15T07:00:00Z", "received_at": "2026-09-15T07:00:01Z", "author_id": "usr_001"}},
        {"log_type": "checkpoint", "metadata": {"creation_date": "2026-09-15T07:10:00Z", "received_at": "2026-09-15T07:10:01Z", "author_id": uid}, "data": {"sequence": 1, "code": "AB"}},
        {"log_type": "checkpoint", "metadata": {"creation_date": "2026-09-15T07:20:00Z", "received_at": "2026-09-15T07:20:01Z", "author_id": uid}, "data": {"sequence": 2, "code": "CD"}},
        {"log_type": "checkpoint", "metadata": {"creation_date": "2026-09-15T07:40:00Z", "received_at": "2026-09-15T07:40:01Z", "author_id": uid}, "data": {"sequence": 3, "code": "EF"}},
        {"log_type": "checkpoint", "metadata": {"creation_date": "2026-09-15T07:55:00Z", "received_at": "2026-09-15T07:55:01Z", "author_id": uid}, "data": {"sequence": 4, "code": "GH"}},
        {"log_type": "checkpoint", "metadata": {"creation_date": "2026-09-15T08:10:00Z", "received_at": "2026-09-15T08:10:01Z", "author_id": uid}, "data": {"sequence": 5, "code": "IJ"}},
    ])
    resp = client.get(f"/api/events/{eid}/resultats", headers=_headers(token))
    comp = resp.json()["competitors"][0]
    assert comp["valid_global"] is True
    assert comp["total_time"] == 4200
    assert comp["sections"][0]["gate"] == "PH1"
    assert comp["sections"][0]["valid"] is True
    assert comp["sections"][1]["valid"] is True
    assert all(b["valid"] is True for b in comp["beacons"])


def test_results_invalid_code() -> None:
    token = _get_token()
    eid = _create_event(token)
    uid = _register(token, eid)
    _write_logs(eid, uid, [
        {"log_type": "departure", "metadata": {"creation_date": "2026-09-15T07:00:00Z", "received_at": "2026-09-15T07:00:01Z", "author_id": "usr_001"}},
        {"log_type": "checkpoint", "metadata": {"creation_date": "2026-09-15T07:10:00Z", "received_at": "2026-09-15T07:10:01Z", "author_id": uid}, "data": {"sequence": 1, "code": "AB"}},
        {"log_type": "checkpoint", "metadata": {"creation_date": "2026-09-15T07:20:00Z", "received_at": "2026-09-15T07:20:01Z", "author_id": uid}, "data": {"sequence": 2, "code": "XX"}},
        {"log_type": "checkpoint", "metadata": {"creation_date": "2026-09-15T07:40:00Z", "received_at": "2026-09-15T07:40:01Z", "author_id": uid}, "data": {"sequence": 3, "code": "EF"}},
        {"log_type": "checkpoint", "metadata": {"creation_date": "2026-09-15T07:55:00Z", "received_at": "2026-09-15T07:55:01Z", "author_id": uid}, "data": {"sequence": 4, "code": "GH"}},
        {"log_type": "checkpoint", "metadata": {"creation_date": "2026-09-15T08:10:00Z", "received_at": "2026-09-15T08:10:01Z", "author_id": uid}, "data": {"sequence": 5, "code": "IJ"}},
    ])
    resp = client.get(f"/api/events/{eid}/resultats", headers=_headers(token))
    comp = resp.json()["competitors"][0]
    assert comp["sections"][0]["valid"] is False
    assert comp["sections"][1]["valid"] is True
    assert comp["valid_global"] is False


def test_results_over_time() -> None:
    token = _get_token()
    eid = _create_event(token)
    uid = _register(token, eid)
    _write_logs(eid, uid, [
        {"log_type": "departure", "metadata": {"creation_date": "2026-09-15T07:00:00Z", "received_at": "2026-09-15T07:00:01Z", "author_id": "usr_001"}},
        {"log_type": "checkpoint", "metadata": {"creation_date": "2026-09-15T07:30:00Z", "received_at": "2026-09-15T07:30:01Z", "author_id": uid}, "data": {"sequence": 1, "code": "AB"}},
        {"log_type": "checkpoint", "metadata": {"creation_date": "2026-09-15T07:50:00Z", "received_at": "2026-09-15T07:50:01Z", "author_id": uid}, "data": {"sequence": 2, "code": "CD"}},
        {"log_type": "checkpoint", "metadata": {"creation_date": "2026-09-15T08:20:00Z", "received_at": "2026-09-15T08:20:01Z", "author_id": uid}, "data": {"sequence": 3, "code": "EF"}},
        {"log_type": "checkpoint", "metadata": {"creation_date": "2026-09-15T08:35:00Z", "received_at": "2026-09-15T08:35:01Z", "author_id": uid}, "data": {"sequence": 4, "code": "GH"}},
        {"log_type": "checkpoint", "metadata": {"creation_date": "2026-09-15T08:50:00Z", "received_at": "2026-09-15T08:50:01Z", "author_id": uid}, "data": {"sequence": 5, "code": "IJ"}},
    ])
    resp = client.get(f"/api/events/{eid}/resultats", headers=_headers(token))
    comp = resp.json()["competitors"][0]
    assert comp["sections"][0]["valid"] is False
    assert comp["sections"][0]["delay"] == 10
    assert comp["sections"][1]["valid"] is True
    assert comp["valid_global"] is False


def test_results_sort_order() -> None:
    token = _get_token()
    eid = _create_event(token)
    uid1 = _register(token, eid, "Alice", "Martin", "F")
    uid2 = _register(token, eid, "Bob", "Durand", "H")
    uid3 = _register(token, eid, "Charlie", "Petit", "H")

    # Alice arrives at 08:30
    _write_logs(eid, uid1, [
        {"log_type": "departure", "metadata": {"creation_date": "2026-09-15T07:00:00Z", "received_at": "2026-09-15T07:00:01Z", "author_id": "usr_001"}},
        {"log_type": "checkpoint", "metadata": {"creation_date": "2026-09-15T07:10:00Z", "received_at": "2026-09-15T07:10:01Z", "author_id": uid1}, "data": {"sequence": 1, "code": "AB"}},
        {"log_type": "checkpoint", "metadata": {"creation_date": "2026-09-15T07:20:00Z", "received_at": "2026-09-15T07:20:01Z", "author_id": uid1}, "data": {"sequence": 2, "code": "CD"}},
        {"log_type": "checkpoint", "metadata": {"creation_date": "2026-09-15T07:40:00Z", "received_at": "2026-09-15T07:40:01Z", "author_id": uid1}, "data": {"sequence": 3, "code": "EF"}},
        {"log_type": "checkpoint", "metadata": {"creation_date": "2026-09-15T07:55:00Z", "received_at": "2026-09-15T07:55:01Z", "author_id": uid1}, "data": {"sequence": 4, "code": "GH"}},
        {"log_type": "checkpoint", "metadata": {"creation_date": "2026-09-15T08:30:00Z", "received_at": "2026-09-15T08:30:01Z", "author_id": uid1}, "data": {"sequence": 5, "code": "IJ"}},
    ])
    # Bob arrives at 08:10 (earlier)
    _write_logs(eid, uid2, [
        {"log_type": "departure", "metadata": {"creation_date": "2026-09-15T07:02:00Z", "received_at": "2026-09-15T07:02:01Z", "author_id": "usr_001"}},
        {"log_type": "checkpoint", "metadata": {"creation_date": "2026-09-15T07:12:00Z", "received_at": "2026-09-15T07:12:01Z", "author_id": uid2}, "data": {"sequence": 1, "code": "AB"}},
        {"log_type": "checkpoint", "metadata": {"creation_date": "2026-09-15T07:22:00Z", "received_at": "2026-09-15T07:22:01Z", "author_id": uid2}, "data": {"sequence": 2, "code": "CD"}},
        {"log_type": "checkpoint", "metadata": {"creation_date": "2026-09-15T07:42:00Z", "received_at": "2026-09-15T07:42:01Z", "author_id": uid2}, "data": {"sequence": 3, "code": "EF"}},
        {"log_type": "checkpoint", "metadata": {"creation_date": "2026-09-15T07:52:00Z", "received_at": "2026-09-15T07:52:01Z", "author_id": uid2}, "data": {"sequence": 4, "code": "GH"}},
        {"log_type": "checkpoint", "metadata": {"creation_date": "2026-09-15T08:10:00Z", "received_at": "2026-09-15T08:10:01Z", "author_id": uid2}, "data": {"sequence": 5, "code": "IJ"}},
    ])
    # Charlie is DNS
    _write_logs(eid, uid3, [
        {"log_type": "dns", "metadata": {"creation_date": "2026-09-15T07:00:00Z", "received_at": "2026-09-15T07:00:01Z", "author_id": "usr_001"}, "data": {"comment": "Absent"}},
    ])

    resp = client.get(f"/api/events/{eid}/resultats", headers=_headers(token))
    comps = resp.json()["competitors"]
    assert comps[0]["first_name"] == "Bob"
    assert comps[1]["first_name"] == "Alice"
    assert comps[2]["first_name"] == "Charlie"
    assert comps[2]["dns"] is True


def test_results_requires_auth() -> None:
    resp = client.get("/api/events/fake-id/resultats")
    assert resp.status_code == 401


def test_results_event_not_found() -> None:
    token = _get_token()
    resp = client.get("/api/events/nonexistent/resultats", headers=_headers(token))
    assert resp.status_code == 404


def test_results_abandoned() -> None:
    token = _get_token()
    eid = _create_event(token)
    uid = _register(token, eid)
    _write_logs(eid, uid, [
        {"log_type": "departure", "metadata": {"creation_date": "2026-09-15T07:00:00Z", "received_at": "2026-09-15T07:00:01Z", "author_id": "usr_001"}},
        {"log_type": "checkpoint", "metadata": {"creation_date": "2026-09-15T07:10:00Z", "received_at": "2026-09-15T07:10:01Z", "author_id": uid}, "data": {"sequence": 1, "code": "AB"}},
        {"log_type": "checkpoint", "metadata": {"creation_date": "2026-09-15T07:20:00Z", "received_at": "2026-09-15T07:20:01Z", "author_id": uid}, "data": {"sequence": 2, "code": "CD"}},
        {"log_type": "checkpoint", "metadata": {"creation_date": "2026-09-15T07:40:00Z", "received_at": "2026-09-15T07:40:01Z", "author_id": uid}, "data": {"sequence": 3, "code": "EF"}},
        {"log_type": "abandon", "metadata": {"creation_date": "2026-09-15T07:50:00Z", "received_at": "2026-09-15T07:50:01Z", "author_id": "usr_001"}, "data": {"comment": "Injury"}},
    ])
    resp = client.get(f"/api/events/{eid}/resultats", headers=_headers(token))
    comp = resp.json()["competitors"][0]
    assert comp["abandoned"] is True
    assert comp["sections"][0]["valid"] is True
    assert comp["sections"][1]["valid"] is None
    assert comp["valid_global"] is None


def test_results_routechoices_url() -> None:
    token = _get_token()
    eid = _create_event(token)
    client.patch(f"/api/events/{eid}", json={"routechoices_url": "https://routechoices.com/test"}, headers=_headers(token))
    resp = client.get(f"/api/events/{eid}/resultats", headers=_headers(token))
    assert resp.json()["routechoices_url"] == "https://routechoices.com/test"

