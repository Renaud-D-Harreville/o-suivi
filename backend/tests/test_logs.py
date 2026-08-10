from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _get_token() -> str:
    response = client.post(
        "/api/auth/login",
        json={"username": "renaud", "password": "arvik"},
    )
    return response.json()["token"]


def _create_event(token: str) -> str:
    response = client.post(
        "/api/events",
        json={"name": "Test Event"},
        headers={"Authorization": f"Bearer {token}"},
    )
    return response.json()["id"]


def _add_registration(token: str, event_id: str) -> str:
    response = client.post(
        f"/api/events/{event_id}/registrations",
        json={
            "first_name": "Marie",
            "last_name": "Dupont",
            "sex": "F",
            "phone": "06 12 34 56 78",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    return response.json()["user_id"]


# --- Departure tests ---


def test_confirm_departure() -> None:
    token = _get_token()
    eid = _create_event(token)
    uid = _add_registration(token, eid)

    response = client.post(
        f"/api/events/{eid}/registrations/{uid}/depart",
        json={"creation_date": "2026-09-15T07:30:12Z"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["log_type"] == "departure"
    assert data["metadata"]["creation_date"] == "2026-09-15T07:30:12Z"
    assert data["metadata"]["author_id"] == "usr_001"
    assert "received_at" in data["metadata"]


def test_cancel_departure() -> None:
    token = _get_token()
    eid = _create_event(token)
    uid = _add_registration(token, eid)

    # First confirm departure
    client.post(
        f"/api/events/{eid}/registrations/{uid}/depart",
        json={"creation_date": "2026-09-15T07:30:12Z"},
        headers={"Authorization": f"Bearer {token}"},
    )

    # Then cancel
    response = client.post(
        f"/api/events/{eid}/registrations/{uid}/depart-cancel",
        json={"creation_date": "2026-09-15T07:31:00Z"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["log_type"] == "departure_cancel"


# --- DNS tests ---


def test_mark_dns() -> None:
    token = _get_token()
    eid = _create_event(token)
    uid = _add_registration(token, eid)

    response = client.post(
        f"/api/events/{eid}/registrations/{uid}/dns",
        json={"creation_date": "2026-09-15T07:00:00Z", "comment": "Pas présent"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["log_type"] == "dns"
    assert data["data"]["comment"] == "Pas présent"


def test_mark_dns_requires_comment() -> None:
    token = _get_token()
    eid = _create_event(token)
    uid = _add_registration(token, eid)

    response = client.post(
        f"/api/events/{eid}/registrations/{uid}/dns",
        json={"creation_date": "2026-09-15T07:00:00Z", "comment": ""},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422


def test_cancel_dns() -> None:
    token = _get_token()
    eid = _create_event(token)
    uid = _add_registration(token, eid)

    client.post(
        f"/api/events/{eid}/registrations/{uid}/dns",
        json={"creation_date": "2026-09-15T07:00:00Z", "comment": "Pas présent"},
        headers={"Authorization": f"Bearer {token}"},
    )

    response = client.post(
        f"/api/events/{eid}/registrations/{uid}/dns-cancel",
        json={"creation_date": "2026-09-15T07:05:00Z", "comment": "Finalement présent"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["log_type"] == "dns_cancel"
    assert data["data"]["comment"] == "Finalement présent"


# --- Bag weight tests ---


def test_record_bag_weight() -> None:
    token = _get_token()
    eid = _create_event(token)
    uid = _add_registration(token, eid)

    response = client.post(
        f"/api/events/{eid}/registrations/{uid}/bag-weight",
        json={
            "creation_date": "2026-09-15T07:25:00Z",
            "moment": "start",
            "weight_kg": 8.5,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["log_type"] == "bag_weight"
    assert data["data"]["moment"] == "start"
    assert data["data"]["weight_kg"] == 8.5


def test_bag_weight_invalid_moment() -> None:
    token = _get_token()
    eid = _create_event(token)
    uid = _add_registration(token, eid)

    response = client.post(
        f"/api/events/{eid}/registrations/{uid}/bag-weight",
        json={
            "creation_date": "2026-09-15T07:25:00Z",
            "moment": "invalid",
            "weight_kg": 8.5,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422


# --- Get logs tests ---


def test_get_logs_empty() -> None:
    token = _get_token()
    eid = _create_event(token)
    uid = _add_registration(token, eid)

    response = client.get(
        f"/api/events/{eid}/registrations/{uid}/logs",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json() == []


def test_get_logs_sorted_by_timestamp() -> None:
    token = _get_token()
    eid = _create_event(token)
    uid = _add_registration(token, eid)

    # Add entries out of order
    client.post(
        f"/api/events/{eid}/registrations/{uid}/depart",
        json={"creation_date": "2026-09-15T07:30:12Z"},
        headers={"Authorization": f"Bearer {token}"},
    )
    client.post(
        f"/api/events/{eid}/registrations/{uid}/bag-weight",
        json={
            "creation_date": "2026-09-15T07:25:00Z",
            "moment": "start",
            "weight_kg": 8.5,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    response = client.get(
        f"/api/events/{eid}/registrations/{uid}/logs",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    logs = response.json()
    assert len(logs) == 2
    # Sorted by creation_date: bag_weight (07:25) comes before departure (07:30)
    assert logs[0]["log_type"] == "bag_weight"
    assert logs[1]["log_type"] == "departure"


# --- PATCH registration tests ---


def test_patch_registration_course_number() -> None:
    token = _get_token()
    eid = _create_event(token)
    uid = _add_registration(token, eid)

    response = client.patch(
        f"/api/events/{eid}/registrations/{uid}",
        json={"course_number": 3},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["course_number"] == 3


def test_patch_registration_start_time() -> None:
    token = _get_token()
    eid = _create_event(token)
    uid = _add_registration(token, eid)

    response = client.patch(
        f"/api/events/{eid}/registrations/{uid}",
        json={"start_time_planned": "08:30"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["start_time_planned"] == "08:30"


def test_patch_registration_tracker() -> None:
    token = _get_token()
    eid = _create_event(token)
    uid = _add_registration(token, eid)

    response = client.patch(
        f"/api/events/{eid}/registrations/{uid}",
        json={"tracker_number": "42"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["tracker_number"] == "42"


def test_patch_registration_not_found() -> None:
    token = _get_token()
    eid = _create_event(token)

    response = client.patch(
        f"/api/events/{eid}/registrations/nonexistent",
        json={"course_number": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


# --- Auth tests ---


def test_departure_requires_auth() -> None:
    token = _get_token()
    eid = _create_event(token)
    uid = _add_registration(token, eid)

    response = client.post(
        f"/api/events/{eid}/registrations/{uid}/depart",
        json={"creation_date": "2026-09-15T07:30:12Z"},
    )
    assert response.status_code == 401


# --- Abandon tests ---


def test_mark_abandon() -> None:
    token = _get_token()
    eid = _create_event(token)
    uid = _add_registration(token, eid)

    response = client.post(
        f"/api/events/{eid}/registrations/{uid}/abandon",
        json={"creation_date": "2026-09-15T09:30:00Z", "comment": "Blessure au genou"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["log_type"] == "abandon"
    assert data["data"]["comment"] == "Blessure au genou"
    assert data["metadata"]["author_id"] == "usr_001"


def test_mark_abandon_requires_comment() -> None:
    token = _get_token()
    eid = _create_event(token)
    uid = _add_registration(token, eid)

    response = client.post(
        f"/api/events/{eid}/registrations/{uid}/abandon",
        json={"creation_date": "2026-09-15T09:30:00Z", "comment": ""},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422


def test_cancel_abandon() -> None:
    token = _get_token()
    eid = _create_event(token)
    uid = _add_registration(token, eid)

    client.post(
        f"/api/events/{eid}/registrations/{uid}/abandon",
        json={"creation_date": "2026-09-15T09:30:00Z", "comment": "Blessure"},
        headers={"Authorization": f"Bearer {token}"},
    )

    response = client.post(
        f"/api/events/{eid}/registrations/{uid}/abandon-cancel",
        json={"creation_date": "2026-09-15T09:35:00Z", "comment": "Fausse alerte"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["log_type"] == "abandon_cancel"
    assert data["data"]["comment"] == "Fausse alerte"


def test_abandon_requires_auth() -> None:
    token = _get_token()
    eid = _create_event(token)
    uid = _add_registration(token, eid)

    response = client.post(
        f"/api/events/{eid}/registrations/{uid}/abandon",
        json={"creation_date": "2026-09-15T09:30:00Z", "comment": "Blessure"},
    )
    assert response.status_code == 401


# --- Tracker returned tests ---


def test_mark_tracker_returned() -> None:
    token = _get_token()
    eid = _create_event(token)
    uid = _add_registration(token, eid)

    response = client.post(
        f"/api/events/{eid}/registrations/{uid}/tracker-returned",
        json={"creation_date": "2026-09-15T11:15:00Z", "tracker_number": "12"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["log_type"] == "tracker_returned"
    assert data["data"]["tracker_number"] == "12"


def test_tracker_returned_requires_tracker_number() -> None:
    token = _get_token()
    eid = _create_event(token)
    uid = _add_registration(token, eid)

    response = client.post(
        f"/api/events/{eid}/registrations/{uid}/tracker-returned",
        json={"creation_date": "2026-09-15T11:15:00Z", "tracker_number": ""},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422


def test_cancel_tracker_returned() -> None:
    token = _get_token()
    eid = _create_event(token)
    uid = _add_registration(token, eid)

    client.post(
        f"/api/events/{eid}/registrations/{uid}/tracker-returned",
        json={"creation_date": "2026-09-15T11:15:00Z", "tracker_number": "12"},
        headers={"Authorization": f"Bearer {token}"},
    )

    response = client.post(
        f"/api/events/{eid}/registrations/{uid}/tracker-returned-cancel",
        json={"creation_date": "2026-09-15T11:20:00Z"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["log_type"] == "tracker_returned_cancel"


def test_tracker_returned_requires_auth() -> None:
    token = _get_token()
    eid = _create_event(token)
    uid = _add_registration(token, eid)

    response = client.post(
        f"/api/events/{eid}/registrations/{uid}/tracker-returned",
        json={"creation_date": "2026-09-15T11:15:00Z", "tracker_number": "12"},
    )
    assert response.status_code == 401


# --- Checkpoint edit tests ---


def test_edit_checkpoint() -> None:
    token = _get_token()
    eid = _create_event(token)
    uid = _add_registration(token, eid)

    response = client.post(
        f"/api/events/{eid}/registrations/{uid}/checkpoint-edit",
        json={
            "creation_date": "2026-09-15T11:00:00Z",
            "passage_time": "2026-09-15T11:00:00Z",
            "sequence": 1,
            "code": "AC",
            "comment": "Erreur de saisie",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["log_type"] == "checkpoint_edit"
    assert data["data"]["sequence"] == 1
    assert data["data"]["code"] == "AC"
    assert data["data"]["comment"] == "Erreur de saisie"


def test_edit_checkpoint_invalid_code_length() -> None:
    token = _get_token()
    eid = _create_event(token)
    uid = _add_registration(token, eid)

    response = client.post(
        f"/api/events/{eid}/registrations/{uid}/checkpoint-edit",
        json={
            "creation_date": "2026-09-15T11:00:00Z",
            "sequence": 1,
            "code": "A",
            "comment": "Trop court",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422


def test_edit_checkpoint_without_comment() -> None:
    token = _get_token()
    eid = _create_event(token)
    uid = _add_registration(token, eid)

    response = client.post(
        f"/api/events/{eid}/registrations/{uid}/checkpoint-edit",
        json={
            "creation_date": "2026-09-15T11:00:00Z",
            "sequence": 1,
            "code": "AC",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["data"]["comment"] is None


def test_edit_checkpoint_requires_auth() -> None:
    token = _get_token()
    eid = _create_event(token)
    uid = _add_registration(token, eid)

    response = client.post(
        f"/api/events/{eid}/registrations/{uid}/checkpoint-edit",
        json={
            "creation_date": "2026-09-15T11:00:00Z",
            "sequence": 1,
            "code": "AC",
            "comment": "Test",
        },
    )
    assert response.status_code == 401


# --- Logs include new types ---


def test_get_logs_includes_abandon_and_tracker() -> None:
    token = _get_token()
    eid = _create_event(token)
    uid = _add_registration(token, eid)

    client.post(
        f"/api/events/{eid}/registrations/{uid}/depart",
        json={"creation_date": "2026-09-15T07:30:00Z"},
        headers={"Authorization": f"Bearer {token}"},
    )
    client.post(
        f"/api/events/{eid}/registrations/{uid}/abandon",
        json={"creation_date": "2026-09-15T09:30:00Z", "comment": "Blessure"},
        headers={"Authorization": f"Bearer {token}"},
    )
    client.post(
        f"/api/events/{eid}/registrations/{uid}/tracker-returned",
        json={"creation_date": "2026-09-15T11:15:00Z", "tracker_number": "5"},
        headers={"Authorization": f"Bearer {token}"},
    )
    client.post(
        f"/api/events/{eid}/registrations/{uid}/checkpoint-edit",
        json={
            "creation_date": "2026-09-15T11:00:00Z",
            "passage_time": "2026-09-15T11:30:00Z",
            "sequence": 2,
            "code": "XY",
            "comment": "Correction",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    response = client.get(
        f"/api/events/{eid}/registrations/{uid}/logs",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    logs = response.json()
    assert len(logs) == 4
    types = [log["log_type"] for log in logs]
    assert "departure" in types
    assert "abandon" in types
    assert "tracker_returned" in types
    assert "checkpoint_edit" in types


def test_edit_checkpoint_time_only() -> None:
    """checkpoint-edit with only a timestamp (no code) should succeed."""
    token = _get_token()
    eid = _create_event(token)
    uid = _add_registration(token, eid)

    response = client.post(
        f"/api/events/{eid}/registrations/{uid}/checkpoint-edit",
        json={
            "creation_date": "2026-09-15T11:00:00Z",
            "passage_time": "2026-09-15T08:30:00",
            "sequence": 4,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["log_type"] == "checkpoint_edit"
    assert data["data"]["passage_time"] == "2026-09-15T08:30:00"
    assert data["data"]["sequence"] == 4
    assert data["data"]["code"] is None


def test_edit_checkpoint_code_only() -> None:
    """checkpoint-edit with only a code (no timestamp) should succeed."""
    token = _get_token()
    eid = _create_event(token)
    uid = _add_registration(token, eid)

    response = client.post(
        f"/api/events/{eid}/registrations/{uid}/checkpoint-edit",
        json={
            "creation_date": "2026-09-15T11:00:00Z",
            "sequence": 4,
            "code": "AB",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["log_type"] == "checkpoint_edit"
    assert data["data"]["passage_time"] is None
    assert data["data"]["sequence"] == 4
    assert data["data"]["code"] == "AB"


def test_edit_checkpoint_time_only_persists_in_logs() -> None:
    """A time-only checkpoint-edit should appear in GET /logs."""
    token = _get_token()
    eid = _create_event(token)
    uid = _add_registration(token, eid)

    client.post(
        f"/api/events/{eid}/registrations/{uid}/checkpoint-edit",
        json={
            "creation_date": "2026-09-15T11:00:00Z",
            "passage_time": "2026-09-15T09:00:00",
            "sequence": 4,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    response = client.get(
        f"/api/events/{eid}/registrations/{uid}/logs",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    logs = response.json()
    assert len(logs) == 1
    assert logs[0]["log_type"] == "checkpoint_edit"
    assert logs[0]["data"]["passage_time"] == "2026-09-15T09:00:00"
    assert logs[0]["data"]["code"] is None


# --- PH Arrival Edit tests ---


def test_ph_arrival_edit_success() -> None:
    token = _get_token()
    eid = _create_event(token)
    uid = _add_registration(token, eid)

    response = client.post(
        f"/api/events/{eid}/registrations/{uid}/ph-arrival-edit",
        json={
            "creation_date": "2026-09-15T08:30:00Z",
            "passage_time": "2026-09-15T08:25:00Z",
            "sequence": 3,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["log_type"] == "ph_arrival_edit"
    assert data["data"]["sequence"] == 3
    assert data["data"]["passage_time"] == "2026-09-15T08:25:00Z"


def test_ph_arrival_edit_updates_ph_arrivals_not_checkpoints() -> None:
    """The ph_arrival_edit log must update ph_arrivals, not checkpoints."""
    token = _get_token()
    eid = _create_event(token)
    uid = _add_registration(token, eid)

    # Post a ph-arrival-edit
    client.post(
        f"/api/events/{eid}/registrations/{uid}/ph-arrival-edit",
        json={
            "creation_date": "2026-09-15T08:30:00Z",
            "passage_time": "2026-09-15T08:25:00Z",
            "sequence": 5,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    # Verify via state reconstruction that it's in ph_arrivals
    from app.domain.competitor_state import CompetitorState
    from app.repositories.log_repository import LogRepository

    logs = LogRepository().load(eid, uid)
    state = CompetitorState()
    for entry in logs:
        entry.apply_to(state)

    assert 5 in state.ph_arrivals
    assert state.ph_arrivals[5] == "08:25:00"
    # Must NOT be in checkpoints
    assert 5 not in state.checkpoints


def test_ph_arrival_edit_missing_passage_time() -> None:
    token = _get_token()
    eid = _create_event(token)
    uid = _add_registration(token, eid)

    response = client.post(
        f"/api/events/{eid}/registrations/{uid}/ph-arrival-edit",
        json={
            "creation_date": "2026-09-15T08:30:00Z",
            "sequence": 3,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422
