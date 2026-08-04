"""Tests for public endpoints (no auth required)."""

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
    resp = client.post("/api/events", json={"name": "Public Test"}, headers=_headers(token))
    event_id = resp.json()["id"]
    client.patch(
        f"/api/events/{event_id}",
        json={
            "date": "2026-09-15",
            "routechoices_url": "https://routechoices.com/test",
            "public_routechoices_time": "14:00",
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


# --- Public events list ---


def test_list_events_no_auth_required() -> None:
    """GET /api/events should be accessible without authentication."""
    resp = client.get("/api/events")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


# --- Public resultats ---


def test_public_results_no_auth_required() -> None:
    """Public results endpoint should be accessible without authentication."""
    token = _get_token()
    eid = _create_event(token)
    resp = client.get(f"/api/public/events/{eid}/resultats")
    assert resp.status_code == 200


def test_public_results_returns_public_routechoices_time() -> None:
    """Public results should include public_routechoices_time and event_date."""
    token = _get_token()
    eid = _create_event(token)
    resp = client.get(f"/api/public/events/{eid}/resultats")
    data = resp.json()
    assert data["public_routechoices_time"] == "14:00"
    assert data["event_date"] == "2026-09-15"
    assert data["routechoices_url"] == "https://routechoices.com/test"


def test_public_results_finished_flag_true() -> None:
    """Competitor who completed all PH should have finished=True."""
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
    resp = client.get(f"/api/public/events/{eid}/resultats")
    comp = resp.json()["competitors"][0]
    assert comp["finished"] is True


def test_public_results_finished_flag_false_when_in_progress() -> None:
    """Competitor still in course should have finished=False."""
    token = _get_token()
    eid = _create_event(token)
    uid = _register(token, eid)
    _write_logs(eid, uid, [
        {"log_type": "departure", "metadata": {"creation_date": "2026-09-15T07:00:00Z", "received_at": "2026-09-15T07:00:01Z", "author_id": "usr_001"}},
        {"log_type": "checkpoint", "metadata": {"creation_date": "2026-09-15T07:10:00Z", "received_at": "2026-09-15T07:10:01Z", "author_id": uid}, "data": {"sequence": 1, "code": "AB"}},
    ])
    resp = client.get(f"/api/public/events/{eid}/resultats")
    comp = resp.json()["competitors"][0]
    assert comp["finished"] is False


def test_public_results_abandoned_is_finished() -> None:
    """Abandoned competitor should have finished=True."""
    token = _get_token()
    eid = _create_event(token)
    uid = _register(token, eid)
    _write_logs(eid, uid, [
        {"log_type": "departure", "metadata": {"creation_date": "2026-09-15T07:00:00Z", "received_at": "2026-09-15T07:00:01Z", "author_id": "usr_001"}},
        {"log_type": "abandon", "metadata": {"creation_date": "2026-09-15T07:30:00Z", "received_at": "2026-09-15T07:30:01Z", "author_id": "usr_001"}, "data": {"comment": "Injury"}},
    ])
    resp = client.get(f"/api/public/events/{eid}/resultats")
    comp = resp.json()["competitors"][0]
    assert comp["finished"] is True
    assert comp["abandoned"] is True


def test_public_results_dns_is_finished() -> None:
    """DNS competitor should have finished=True."""
    token = _get_token()
    eid = _create_event(token)
    uid = _register(token, eid)
    _write_logs(eid, uid, [
        {"log_type": "dns", "metadata": {"creation_date": "2026-09-15T07:00:00Z", "received_at": "2026-09-15T07:00:01Z", "author_id": "usr_001"}, "data": {"comment": "No show"}},
    ])
    resp = client.get(f"/api/public/events/{eid}/resultats")
    comp = resp.json()["competitors"][0]
    assert comp["finished"] is True
    assert comp["dns"] is True


def test_public_results_has_tracker_false_by_default() -> None:
    """Competitor without tracker should have has_tracker=False."""
    token = _get_token()
    eid = _create_event(token)
    uid = _register(token, eid)
    resp = client.get(f"/api/public/events/{eid}/resultats")
    comp = resp.json()["competitors"][0]
    assert comp["has_tracker"] is False
    assert comp["tracker_returned"] is False


def test_public_results_has_tracker_true_when_assigned() -> None:
    """Competitor with tracker_number should have has_tracker=True."""
    token = _get_token()
    eid = _create_event(token)
    uid = _register(token, eid)
    client.patch(
        f"/api/events/{eid}/registrations/{uid}",
        json={"tracker_number": "12"},
        headers=_headers(token),
    )
    resp = client.get(f"/api/public/events/{eid}/resultats")
    comp = resp.json()["competitors"][0]
    assert comp["has_tracker"] is True
    assert comp["tracker_returned"] is False


def test_public_results_tracker_returned_true() -> None:
    """Competitor who returned tracker should have tracker_returned=True."""
    token = _get_token()
    eid = _create_event(token)
    uid = _register(token, eid)
    client.patch(
        f"/api/events/{eid}/registrations/{uid}",
        json={"tracker_number": "12"},
        headers=_headers(token),
    )
    _write_logs(eid, uid, [
        {"log_type": "tracker_returned", "metadata": {"creation_date": "2026-09-15T10:00:00Z", "received_at": "2026-09-15T10:00:01Z", "author_id": "usr_001"}, "data": {"tracker_number": "12"}},
    ])
    resp = client.get(f"/api/public/events/{eid}/resultats")
    comp = resp.json()["competitors"][0]
    assert comp["has_tracker"] is True
    assert comp["tracker_returned"] is True


# --- Public checkpoints ---


def test_public_checkpoints_no_auth() -> None:
    """Public checkpoints endpoint should work without auth."""
    token = _get_token()
    eid = _create_event(token)
    uid = _register(token, eid)
    _write_logs(eid, uid, [
        {"log_type": "checkpoint", "metadata": {"creation_date": "2026-09-15T07:10:00Z", "received_at": "2026-09-15T07:10:01Z", "author_id": uid}, "data": {"sequence": 1, "code": "AB"}},
    ])
    resp = client.get(f"/api/public/events/{eid}/competitors/{uid}/checkpoints")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["checkpoints"]) == 1
    assert data["checkpoints"][0]["code"] == "AB"


def test_public_checkpoints_includes_ph_arrivals() -> None:
    """Public checkpoints should include ph_arrivals."""
    token = _get_token()
    eid = _create_event(token)
    uid = _register(token, eid)
    _write_logs(eid, uid, [
        {"log_type": "ph_arrival", "metadata": {"creation_date": "2026-09-15T07:38:00Z", "received_at": "2026-09-15T07:38:01Z", "author_id": uid}, "data": {"sequence": 3}},
        {"log_type": "checkpoint", "metadata": {"creation_date": "2026-09-15T07:40:00Z", "received_at": "2026-09-15T07:40:01Z", "author_id": uid}, "data": {"sequence": 3, "code": "EF"}},
    ])
    resp = client.get(f"/api/public/events/{eid}/competitors/{uid}/checkpoints")
    data = resp.json()
    assert "3" in data["ph_arrivals"] or 3 in data["ph_arrivals"]
    assert data["checkpoints"][0]["code"] == "EF"


# --- Public checkpoint edit ---


def test_public_checkpoint_edit_no_auth() -> None:
    """Public checkpoint-edit should work without auth and use author_id='public'."""
    token = _get_token()
    eid = _create_event(token)
    uid = _register(token, eid)

    resp = client.post(
        f"/api/public/events/{eid}/competitors/{uid}/checkpoint-edit",
        json={"creation_date": "2026-09-15T10:00:00Z", "sequence": 1, "code": "AB", "passage_time": "2026-09-15T07:10:00Z"},
    )
    assert resp.status_code == 201
    entry = resp.json()
    assert entry["metadata"]["author_id"] == "public"
    assert entry["data"]["code"] == "AB"
    assert entry["data"]["sequence"] == 1


def test_public_checkpoint_edit_persists() -> None:
    """After a public edit, the checkpoint should appear in GET checkpoints."""
    token = _get_token()
    eid = _create_event(token)
    uid = _register(token, eid)

    client.post(
        f"/api/public/events/{eid}/competitors/{uid}/checkpoint-edit",
        json={"creation_date": "2026-09-15T10:00:00Z", "sequence": 2, "code": "CD", "passage_time": "2026-09-15T07:20:00Z"},
    )
    resp = client.get(f"/api/public/events/{eid}/competitors/{uid}/checkpoints")
    data = resp.json()
    assert len(data["checkpoints"]) == 1
    assert data["checkpoints"][0]["code"] == "CD"


def test_public_checkpoint_edit_null_code() -> None:
    """Public edit with null code should clear the code."""
    token = _get_token()
    eid = _create_event(token)
    uid = _register(token, eid)

    resp = client.post(
        f"/api/public/events/{eid}/competitors/{uid}/checkpoint-edit",
        json={"creation_date": "2026-09-15T10:00:00Z", "sequence": 1, "code": None, "passage_time": "2026-09-15T07:10:00Z"},
    )
    assert resp.status_code == 201
    assert resp.json()["data"]["code"] is None


def test_public_ph_arrival_edit() -> None:
    """Public ph-arrival-edit should work without auth and store in ph_arrivals."""
    token = _get_token()
    eid = _create_event(token)
    uid = _register(token, eid)

    resp = client.post(
        f"/api/public/events/{eid}/competitors/{uid}/ph-arrival-edit",
        json={
            "creation_date": "2026-09-15T09:00:00Z",
            "passage_time": "2026-09-15T08:55:00Z",
            "sequence": 3,
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["log_type"] == "ph_arrival_edit"
    assert data["data"]["sequence"] == 3
    assert data["data"]["passage_time"] == "2026-09-15T08:55:00Z"
    assert data["metadata"]["author_id"] == "public"


# --- Public splits ---


def test_public_splits_no_auth_required() -> None:
    """Public splits endpoint should be accessible without authentication."""
    token = _get_token()
    eid = _create_event(token)
    resp = client.get(f"/api/public/events/{eid}/splits")
    assert resp.status_code == 200
    data = resp.json()
    assert "pairs" in data
    assert "beacons" in data
    assert "competitors" in data
    assert data["event_name"] == "Public Test"


def test_public_splits_returns_pairs_for_course() -> None:
    """Splits should return correct beacon pairs for the configured course."""
    token = _get_token()
    eid = _create_event(token)
    resp = client.get(f"/api/public/events/{eid}/splits")
    data = resp.json()
    # Course 1 has beacons [31, 32, 33, 34, 35]
    # Pairs: (None→31), (31→32), (32→33), (33→34), (34→35)
    assert len(data["pairs"]) == 5
    assert data["pairs"][0]["from_beacon_id"] is None
    assert data["pairs"][0]["to_beacon_id"] == 31


def test_public_splits_computes_split_times() -> None:
    """Splits should compute correct split times for competitors."""
    token = _get_token()
    eid = _create_event(token)
    uid = _register(token, eid)
    _write_logs(eid, uid, [
        {"log_type": "departure", "metadata": {"creation_date": "2026-09-15T07:00:00Z", "received_at": "2026-09-15T07:00:01Z", "author_id": "usr_001"}},
        {"log_type": "checkpoint", "metadata": {"creation_date": "2026-09-15T07:10:00Z", "received_at": "2026-09-15T07:10:01Z", "author_id": uid}, "data": {"sequence": 1, "code": "AB"}},
        {"log_type": "checkpoint", "metadata": {"creation_date": "2026-09-15T07:25:00Z", "received_at": "2026-09-15T07:25:01Z", "author_id": uid}, "data": {"sequence": 2, "code": "CD"}},
    ])
    resp = client.get(f"/api/public/events/{eid}/splits")
    data = resp.json()

    # First pair: Départ → Balise 1 = 10 min = 600 sec
    first_pair = data["pairs"][0]
    assert first_pair["from_beacon_id"] is None
    assert first_pair["to_beacon_id"] == 31
    assert len(first_pair["splits"]) == 1
    assert first_pair["splits"][0]["user_id"] == uid
    assert first_pair["splits"][0]["split_seconds"] == 600

    # Second pair: Balise 1 → Balise 2 = 15 min = 900 sec
    second_pair = data["pairs"][1]
    assert second_pair["from_beacon_id"] == 31
    assert second_pair["to_beacon_id"] == 32
    assert len(second_pair["splits"]) == 1
    assert second_pair["splits"][0]["split_seconds"] == 900


def test_public_splits_sorted_by_time() -> None:
    """Splits within a pair should be sorted by split_seconds (fastest first)."""
    token = _get_token()
    eid = _create_event(token)
    uid1 = _register(token, eid, first="Alice", last="Fast")
    uid2 = _register(token, eid, first="Bob", last="Slow")

    # Alice: 10 min to beacon 1
    _write_logs(eid, uid1, [
        {"log_type": "departure", "metadata": {"creation_date": "2026-09-15T07:00:00Z", "received_at": "2026-09-15T07:00:01Z", "author_id": "usr_001"}},
        {"log_type": "checkpoint", "metadata": {"creation_date": "2026-09-15T07:10:00Z", "received_at": "2026-09-15T07:10:01Z", "author_id": uid1}, "data": {"sequence": 1, "code": "AB"}},
    ])
    # Bob: 20 min to beacon 1
    _write_logs(eid, uid2, [
        {"log_type": "departure", "metadata": {"creation_date": "2026-09-15T07:00:00Z", "received_at": "2026-09-15T07:00:01Z", "author_id": "usr_001"}},
        {"log_type": "checkpoint", "metadata": {"creation_date": "2026-09-15T07:20:00Z", "received_at": "2026-09-15T07:20:01Z", "author_id": uid2}, "data": {"sequence": 1, "code": "AB"}},
    ])

    resp = client.get(f"/api/public/events/{eid}/splits")
    first_pair = resp.json()["pairs"][0]
    assert len(first_pair["splits"]) == 2
    assert first_pair["splits"][0]["user_id"] == uid1  # Alice first (faster)
    assert first_pair["splits"][0]["split_seconds"] == 600
    assert first_pair["splits"][1]["user_id"] == uid2  # Bob second (slower)
    assert first_pair["splits"][1]["split_seconds"] == 1200


def test_public_splits_excludes_dns() -> None:
    """DNS competitors should be excluded from splits."""
    token = _get_token()
    eid = _create_event(token)
    uid = _register(token, eid)
    _write_logs(eid, uid, [
        {"log_type": "dns", "metadata": {"creation_date": "2026-09-15T07:00:00Z", "received_at": "2026-09-15T07:00:01Z", "author_id": "usr_001"}, "data": {"comment": "No show"}},
    ])
    resp = client.get(f"/api/public/events/{eid}/splits")
    data = resp.json()
    assert len(data["competitors"]) == 0


