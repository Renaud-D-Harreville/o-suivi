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


def test_list_registrations_empty() -> None:
    token = _get_token()
    eid = _create_event(token)
    response = client.get(
        f"/api/events/{eid}/registrations",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json() == []


def test_add_registration() -> None:
    token = _get_token()
    eid = _create_event(token)
    response = client.post(
        f"/api/events/{eid}/registrations",
        json={"first_name": "Marie", "last_name": "Dupont", "sex": "F", "phone": "06 12"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "Marie"
    assert data["last_name"] == "Dupont"
    assert data["sex"] == "F"
    assert "user_id" in data


def test_add_then_list() -> None:
    token = _get_token()
    eid = _create_event(token)
    client.post(
        f"/api/events/{eid}/registrations",
        json={"first_name": "Marie", "last_name": "Dupont", "sex": "F", "phone": ""},
        headers={"Authorization": f"Bearer {token}"},
    )
    client.post(
        f"/api/events/{eid}/registrations",
        json={"first_name": "Pierre", "last_name": "Martin", "sex": "H", "phone": ""},
        headers={"Authorization": f"Bearer {token}"},
    )
    response = client.get(
        f"/api/events/{eid}/registrations",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    names = [r["last_name"] for r in response.json()]
    assert "Dupont" in names
    assert "Martin" in names


def test_add_duplicate_registration() -> None:
    token = _get_token()
    eid = _create_event(token)
    client.post(
        f"/api/events/{eid}/registrations",
        json={"first_name": "Marie", "last_name": "Dupont", "sex": "F", "phone": ""},
        headers={"Authorization": f"Bearer {token}"},
    )
    response = client.post(
        f"/api/events/{eid}/registrations",
        json={"first_name": "Marie", "last_name": "Dupont", "sex": "F", "phone": ""},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 409


def test_remove_registration() -> None:
    token = _get_token()
    eid = _create_event(token)
    res = client.post(
        f"/api/events/{eid}/registrations",
        json={"first_name": "Marie", "last_name": "Dupont", "sex": "F", "phone": ""},
        headers={"Authorization": f"Bearer {token}"},
    )
    uid = res.json()["user_id"]
    response = client.delete(
        f"/api/events/{eid}/registrations/{uid}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 204

    # Verify list is empty
    list_res = client.get(
        f"/api/events/{eid}/registrations",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert list_res.json() == []


def test_remove_registration_not_found() -> None:
    token = _get_token()
    eid = _create_event(token)
    response = client.delete(
        f"/api/events/{eid}/registrations/nonexistent",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


def test_registrations_require_auth() -> None:
    response = client.get("/api/events/some-id/registrations")
    assert response.status_code == 401

    response = client.post(
        "/api/events/some-id/registrations",
        json={"first_name": "X", "last_name": "Y", "sex": "H"},
    )
    assert response.status_code == 401


def test_bulk_save_registrations() -> None:
    token = _get_token()
    eid = _create_event(token)
    body = [
        {"first_name": "Marie", "last_name": "Dupont", "sex": "F", "phone": "06 12"},
        {"first_name": "Pierre", "last_name": "Martin", "sex": "H", "phone": "06 34"},
    ]
    response = client.put(
        f"/api/events/{eid}/registrations",
        json=body,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["first_name"] == "Marie"
    assert data[1]["last_name"] == "Martin"


def test_bulk_save_updates_existing() -> None:
    token = _get_token()
    eid = _create_event(token)
    # First save
    client.put(
        f"/api/events/{eid}/registrations",
        json=[{"first_name": "Marie", "last_name": "Dupont", "sex": "F", "phone": "old"}],
        headers={"Authorization": f"Bearer {token}"},
    )
    # Update phone
    response = client.put(
        f"/api/events/{eid}/registrations",
        json=[{"first_name": "Marie", "last_name": "Dupont", "sex": "F", "phone": "new"}],
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()[0]["phone"] == "new"
    # Should still have only 1 registration
    list_res = client.get(
        f"/api/events/{eid}/registrations",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert len(list_res.json()) == 1


def test_bulk_save_removes_absent() -> None:
    token = _get_token()
    eid = _create_event(token)
    # Save 2 participants
    client.put(
        f"/api/events/{eid}/registrations",
        json=[
            {"first_name": "Marie", "last_name": "Dupont", "sex": "F", "phone": ""},
            {"first_name": "Pierre", "last_name": "Martin", "sex": "H", "phone": ""},
        ],
        headers={"Authorization": f"Bearer {token}"},
    )
    # Save with only 1 — Pierre should be removed
    client.put(
        f"/api/events/{eid}/registrations",
        json=[{"first_name": "Marie", "last_name": "Dupont", "sex": "F", "phone": ""}],
        headers={"Authorization": f"Bearer {token}"},
    )
    list_res = client.get(
        f"/api/events/{eid}/registrations",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert len(list_res.json()) == 1
    assert list_res.json()[0]["first_name"] == "Marie"


def test_add_registration_with_routechoices_id() -> None:
    token = _get_token()
    eid = _create_event(token)
    response = client.post(
        f"/api/events/{eid}/registrations",
        json={
            "first_name": "Marie",
            "last_name": "Dupont",
            "sex": "F",
            "phone": "06 12",
            "routechoices_id": "rc_123",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["routechoices_id"] == "rc_123"


def test_list_registrations_includes_routechoices_id() -> None:
    token = _get_token()
    eid = _create_event(token)
    client.post(
        f"/api/events/{eid}/registrations",
        json={
            "first_name": "Marie",
            "last_name": "Dupont",
            "sex": "F",
            "phone": "",
            "routechoices_id": "rc_456",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    response = client.get(
        f"/api/events/{eid}/registrations",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()[0]["routechoices_id"] == "rc_456"


def test_bulk_save_deduplicates_by_routechoices_id() -> None:
    """When routechoices_id matches, user is updated even if name changed."""
    token = _get_token()
    eid = _create_event(token)
    # First save with routechoices_id
    client.put(
        f"/api/events/{eid}/registrations",
        json=[{
            "first_name": "Marie",
            "last_name": "Dupont",
            "sex": "F",
            "phone": "old",
            "routechoices_id": "rc_999",
        }],
        headers={"Authorization": f"Bearer {token}"},
    )
    # Save again with same routechoices_id but different name
    response = client.put(
        f"/api/events/{eid}/registrations",
        json=[{
            "first_name": "Marie-Claire",
            "last_name": "Dupont-Martin",
            "sex": "F",
            "phone": "new",
            "routechoices_id": "rc_999",
        }],
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["first_name"] == "Marie-Claire"
    assert data[0]["last_name"] == "Dupont-Martin"
    assert data[0]["phone"] == "new"
    # Should still be 1 registration (not a duplicate)
    list_res = client.get(
        f"/api/events/{eid}/registrations",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert len(list_res.json()) == 1


def test_bulk_save_routechoices_id_priority_over_name() -> None:
    """routechoices_id deduplication takes priority over name match."""
    token = _get_token()
    eid = _create_event(token)
    # Save two participants: one with rc_id, one without
    client.put(
        f"/api/events/{eid}/registrations",
        json=[
            {"first_name": "Marie", "last_name": "Dupont", "sex": "F", "phone": "", "routechoices_id": "rc_aaa"},
            {"first_name": "Pierre", "last_name": "Martin", "sex": "H", "phone": "", "routechoices_id": ""},
        ],
        headers={"Authorization": f"Bearer {token}"},
    )
    # Update: match by rc_id (Marie's name changes), Pierre matched by name
    response = client.put(
        f"/api/events/{eid}/registrations",
        json=[
            {"first_name": "Marie-Updated", "last_name": "Dupont", "sex": "F", "phone": "new", "routechoices_id": "rc_aaa"},
            {"first_name": "Pierre", "last_name": "Martin", "sex": "H", "phone": "new2", "routechoices_id": ""},
        ],
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    # Verify both were updated (not duplicated)
    list_res = client.get(
        f"/api/events/{eid}/registrations",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert len(list_res.json()) == 2


def _add_registration(token: str, eid: str) -> str:
    res = client.post(
        f"/api/events/{eid}/registrations",
        json={"first_name": "Marie", "last_name": "Dupont", "sex": "F", "phone": ""},
        headers={"Authorization": f"Bearer {token}"},
    )
    return res.json()["user_id"]


def test_get_checkpoints_empty() -> None:
    token = _get_token()
    eid = _create_event(token)
    uid = _add_registration(token, eid)
    response = client.get(
        f"/api/events/{eid}/registrations/{uid}/checkpoints",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json() == []


def test_get_checkpoints_after_edit() -> None:
    token = _get_token()
    eid = _create_event(token)
    uid = _add_registration(token, eid)

    # Record a checkpoint edit
    client.post(
        f"/api/events/{eid}/registrations/{uid}/checkpoint-edit",
        json={"creation_date": "2026-09-15T12:00:00Z", "passage_time": "2026-09-15T12:49:00", "sequence": 3, "code": "AB"},
        headers={"Authorization": f"Bearer {token}"},
    )

    response = client.get(
        f"/api/events/{eid}/registrations/{uid}/checkpoints",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["sequence"] == 3
    assert data[0]["code"] == "AB"
    assert data[0]["passage_time"] == "2026-09-15T12:49:00"


def test_get_checkpoints_edit_overwrites_previous() -> None:
    """A checkpoint_edit with an earlier passage time should still overwrite."""
    token = _get_token()
    eid = _create_event(token)
    uid = _add_registration(token, eid)

    # First: checkpoint at 13:05
    client.post(
        f"/api/events/{eid}/registrations/{uid}/checkpoint-edit",
        json={"creation_date": "2026-09-15T12:00:00Z", "passage_time": "2026-09-15T13:05:00", "sequence": 3, "code": "AB"},
        headers={"Authorization": f"Bearer {token}"},
    )
    # Then: edit to correct time to 12:49
    client.post(
        f"/api/events/{eid}/registrations/{uid}/checkpoint-edit",
        json={"creation_date": "2026-09-15T12:00:00Z", "passage_time": "2026-09-15T12:49:00", "sequence": 3, "code": "AB"},
        headers={"Authorization": f"Bearer {token}"},
    )

    response = client.get(
        f"/api/events/{eid}/registrations/{uid}/checkpoints",
        headers={"Authorization": f"Bearer {token}"},
    )
    data = response.json()
    assert len(data) == 1
    # The second edit (12:49) should win, even though its passage_time is earlier
    assert data[0]["passage_time"] == "2026-09-15T12:49:00"

